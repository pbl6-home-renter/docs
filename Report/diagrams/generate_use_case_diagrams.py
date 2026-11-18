import math
import os
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FS = 19
FS_SMALL = 16
FS_TITLE = 24
SCALE = 2
LINE_W = 2

ROW_H = 88
OVAL_W, OVAL_H = 340, 64
REL_W = 330
GAP_X = 190
GROUP_PAD_X = 60
GROUP_PAD_Y = 22
GROUP_GAP = 46
TAB_H = 26

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _fonts[key]


def text_w(s, size, bold=False):
    return font(size, bold).getlength(s)


def wrap(s, max_w, size):
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, size) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


class Canvas:
    def __init__(self):
        self.ops = []

    def rect(self, x, y, w, h):
        self.ops.append(("rect", x, y, w, h))

    def ellipse(self, cx, cy, a, b):
        self.ops.append(("ellipse", cx, cy, a, b))

    def line(self, p, q, dashed=False):
        self.ops.append(("line", p, q, dashed))

    def arrow_head(self, tip, frm):
        ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
        for d in (math.radians(25), -math.radians(25)):
            self.line(
                tip,
                (tip[0] - 15 * math.cos(ang - d), tip[1] - 15 * math.sin(ang - d)),
            )

    def text(self, x, y, s, size=FS, bold=False, white_bg=False):
        self.ops.append(("text", x, y, s, size, bold, white_bg))

    def stickman(self, x, y, name):
        self.ops.append(("man", x, y, name))

    def bounds(self):
        xs, ys = [0], [0]
        for op in self.ops:
            if op[0] == "rect":
                xs += [op[1] + op[3]]
                ys += [op[2] + op[4]]
            elif op[0] == "ellipse":
                xs += [op[1] + op[3]]
                ys += [op[2] + op[4]]
            elif op[0] == "man":
                xs += [op[1] + 80]
                ys += [op[2] + 80]
        return max(xs) + 40, max(ys) + 40

    def save(self, name):
        W, H = self.bounds()
        self._svg(os.path.join(OUT_DIR, name + ".svg"), W, H)
        self._png(os.path.join(OUT_DIR, name + ".png"), W, H)

    def _svg(self, path, W, H):
        o = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" font-family="Arial, sans-serif">',
            '<rect width="100%" height="100%" fill="white"/>',
        ]
        st = f'fill="none" stroke="black" stroke-width="{LINE_W}"'
        for op in self.ops:
            k = op[0]
            if k == "rect":
                o.append(f'<rect x="{op[1]:.1f}" y="{op[2]:.1f}" width="{op[3]:.1f}" height="{op[4]:.1f}" {st}/>')
            elif k == "ellipse":
                o.append(f'<ellipse cx="{op[1]:.1f}" cy="{op[2]:.1f}" rx="{op[3]:.1f}" ry="{op[4]:.1f}" fill="white" stroke="black" stroke-width="{LINE_W}"/>')
            elif k == "line":
                d = ' stroke-dasharray="9 7"' if op[3] else ""
                o.append(f'<line x1="{op[1][0]:.1f}" y1="{op[1][1]:.1f}" x2="{op[2][0]:.1f}" y2="{op[2][1]:.1f}" stroke="black" stroke-width="{LINE_W}"{d}/>')
            elif k == "text":
                _, x, y, s, size, bold, bg = op
                lines = s.split("\n")
                lh = size * 1.25
                y0 = y - lh * (len(lines) - 1) / 2
                if bg:
                    w = max(text_w(l, size, bold) for l in lines) + 10
                    h = lh * len(lines) + 4
                    o.append(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="white"/>')
                for i, l in enumerate(lines):
                    wt = ' font-weight="bold"' if bold else ""
                    o.append(f'<text x="{x:.1f}" y="{y0 + i * lh:.1f}" font-size="{size}"{wt} text-anchor="middle" dominant-baseline="central">{escape(l)}</text>')
            elif k == "man":
                _, x, y, name = op
                o += man_svg(x, y, name)
        o.append("</svg>")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(o))

    def _png(self, path, W, H):
        img = Image.new("RGB", (int(W * SCALE), int(H * SCALE)), "white")
        d = ImageDraw.Draw(img)
        S = SCALE
        lw = LINE_W * S
        for op in self.ops:
            k = op[0]
            if k == "rect":
                _, x, y, w, h = op
                d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], outline="black", width=lw)
            elif k == "ellipse":
                _, cx, cy, a, b = op
                d.ellipse([(cx - a) * S, (cy - b) * S, (cx + a) * S, (cy + b) * S], fill="white", outline="black", width=lw)
            elif k == "line":
                _, p, q, dashed = op
                if not dashed:
                    d.line([p[0] * S, p[1] * S, q[0] * S, q[1] * S], fill="black", width=lw)
                else:
                    L = math.dist(p, q)
                    n = int(L // 16) + 1
                    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
                    for i in range(n):
                        s0, s1 = i * 16, min(i * 16 + 9, L)
                        d.line([(p[0] + ux * s0) * S, (p[1] + uy * s0) * S, (p[0] + ux * s1) * S, (p[1] + uy * s1) * S], fill="black", width=lw)
            elif k == "text":
                _, x, y, s, size, bold, bg = op
                f = font(size * S, bold)
                lines = s.split("\n")
                lh = size * 1.25
                y0 = y - lh * (len(lines) - 1) / 2
                if bg:
                    w = max(text_w(l, size, bold) for l in lines) + 10
                    h = lh * len(lines) + 4
                    d.rectangle([(x - w / 2) * S, (y - h / 2) * S, (x + w / 2) * S, (y + h / 2) * S], fill="white")
                for i, l in enumerate(lines):
                    d.text((x * S, (y0 + i * lh) * S), l, font=f, fill="black", anchor="mm")
            elif k == "man":
                _, x, y, name = op
                man_png(d, x, y, name)
        img.save(path, dpi=(200, 200))


def man_svg(x, y, name):
    st = f'fill="none" stroke="black" stroke-width="{LINE_W}"'
    out = [
        f'<circle cx="{x:.1f}" cy="{y - 38:.1f}" r="13" fill="white" stroke="black" stroke-width="{LINE_W}"/>',
        f'<line x1="{x}" y1="{y - 25}" x2="{x}" y2="{y + 14}" stroke="black" stroke-width="{LINE_W}"/>',
        f'<line x1="{x - 24}" y1="{y - 12}" x2="{x + 24}" y2="{y - 12}" stroke="black" stroke-width="{LINE_W}"/>',
        f'<line x1="{x}" y1="{y + 14}" x2="{x - 22}" y2="{y + 48}" stroke="black" stroke-width="{LINE_W}"/>',
        f'<line x1="{x}" y1="{y + 14}" x2="{x + 22}" y2="{y + 48}" stroke="black" stroke-width="{LINE_W}"/>',
    ]
    lines = name.split("\n")
    for i, l in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + 72 + i * 22}" font-size="{FS}" font-weight="bold" text-anchor="middle" dominant-baseline="central">{escape(l)}</text>')
    return out


def man_png(d, x, y, name):
    S, lw = SCALE, LINE_W * SCALE
    d.ellipse([(x - 13) * S, (y - 51) * S, (x + 13) * S, (y - 25) * S], fill="white", outline="black", width=lw)
    for a, b, c, e in [(x, y - 25, x, y + 14), (x - 24, y - 12, x + 24, y - 12), (x, y + 14, x - 22, y + 48), (x, y + 14, x + 22, y + 48)]:
        d.line([a * S, b * S, c * S, e * S], fill="black", width=lw)
    for i, l in enumerate(name.split("\n")):
        d.text((x * S, (y + 72 + i * 22) * S), l, font=font(FS * S, True), fill="black", anchor="mm")


def clip_ellipse(c, ell, toward):
    cx, cy, a, b = ell
    dx, dy = toward[0] - cx, toward[1] - cy
    t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
    return (cx + dx * t, cy + dy * t)


def draw_oval(cv, cx, cy, w, label):
    a, b = w / 2, OVAL_H / 2
    cv.ellipse(cx, cy, a, b)
    cv.text(cx, cy, "\n".join(wrap(label, w - 80, FS)))
    return (cx, cy, a, b)


def draw_relation(cv, base, rel, kind):
    src, dst = (base, rel) if kind == "include" else (rel, base)
    p = clip_ellipse(cv, src, (dst[0], dst[1]))
    q = clip_ellipse(cv, dst, (src[0], src[1]))
    cv.line(p, q, dashed=True)
    cv.arrow_head(q, p)
    label = "«include»" if kind == "include" else "«extend»"
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    if abs(p[1] - q[1]) < 2:
        cv.text(mx, my - 14, label, FS_SMALL)
    else:
        cv.text(mx, my, label, FS_SMALL, white_bg=True)


def actor_diagram(name, system_title, actor_label, groups, filename):
    cv = Canvas()
    ax = 110
    colA_cx = ax + 470 + GROUP_PAD_X + OVAL_W / 2
    colB_cx = colA_cx + OVAL_W / 2 + GAP_X + REL_W / 2
    box_l = colA_cx - OVAL_W / 2 - GROUP_PAD_X
    box_r = colB_cx + REL_W / 2 + GROUP_PAD_X
    sys_l, sys_r = box_l - 50, box_r + 50
    y = 90
    placed = []
    boxes = []
    for g in groups:
        max_row = max([r for _, _, r in g["bases"]] + [r for _, _, r in g["rel"]])
        top = y + TAB_H
        h = (max_row + 1) * ROW_H + GROUP_PAD_Y * 2 - (ROW_H - OVAL_H)
        boxes.append((g["title"], box_l, top, box_r - box_l, h))
        els = {}
        for i, (key, label, r) in enumerate(g["bases"]):
            cy = top + GROUP_PAD_Y + OVAL_H / 2 + r * ROW_H
            els[key] = ("base", colA_cx, cy, OVAL_W, label)
        for key, label, r in g["rel"]:
            cy = top + GROUP_PAD_Y + OVAL_H / 2 + r * ROW_H
            els[key] = ("rel", colB_cx, cy, REL_W, label)
        placed.append((g, els))
        y = top + h + GROUP_GAP
    sys_bottom = y - GROUP_GAP + 36
    cv.rect(sys_l, 28, sys_r - sys_l, sys_bottom - 28)
    cv.text((sys_l + sys_r) / 2, 54, system_title, FS_TITLE, bold=True)
    for title, x, yy, w, h in boxes:
        cv.rect(x, yy, w, h)
        tw = text_w(title, FS_SMALL, True) + 28
        cv.rect(x + w - tw, yy - TAB_H, tw, TAB_H)
        cv.text(x + w - tw / 2, yy - TAB_H / 2, title, FS_SMALL, bold=True)
    mid = (28 + sys_bottom) / 2
    ay = mid - 20
    origin = (ax + 26, ay - 12)
    ellipses = {}
    for g, els in placed:
        for key, (kind, cx, cy, w, label) in els.items():
            ellipses[key] = draw_oval(cv, cx, cy, w, label)
        for key, (kind, cx, cy, w, label) in els.items():
            if kind == "base":
                e = ellipses[key]
                cv.line(origin, (e[0] - e[2], e[1]))
        for src, dst, kind in g["links"]:
            draw_relation(cv, ellipses[src], ellipses[dst], kind)
    cv.stickman(ax, ay, actor_label)
    cv.save(filename)


def general_diagram(filename):
    pk = [
        "1. Tài khoản và xác thực",
        "2. Trò chuyện và thông báo",
        "3. Quản trị hệ thống",
        "4. Khám phá phòng trọ",
        "5. Quản lý tòa nhà và phòng",
        "6. Hợp đồng và thành viên",
        "7. Biểu giá và chỉ số điện nước",
        "8. Hóa đơn và thanh toán",
        "9. Sự cố và tệp đính kèm",
        "10. Tìm bạn ở ghép",
    ]
    summary = [
        "Đăng ký, đăng nhập, quên mật khẩu, hồ sơ cá nhân",
        "Trò chuyện, thông báo đẩy, tùy chỉnh thông báo",
        "Duyệt bất động sản, quản lý tài khoản, nhật ký, thống kê",
        "Tìm và xem phòng, tòa nhà theo khu vực",
        "Quản lý tòa nhà và phòng, đánh dấu sẵn sàng cho thuê",
        "Lập và kích hoạt hợp đồng, quản lý thành viên, trả phòng",
        "Biểu giá, kỳ lập hóa đơn, ghi chỉ số điện nước",
        "Lập hóa đơn, thanh toán QR, tiền mặt, đối soát",
        "Báo cáo, theo dõi và xử lý sự cố, đính kèm ảnh",
        "Hồ sơ ở ghép, tìm bạn, yêu cầu ghép đôi",
    ]
    links = {
        "guest": [0, 3],
        "tenant": [0, 1, 3, 5, 7, 8, 9],
        "landlord": [0, 1, 4, 5, 6, 7, 8],
        "admin": [0, 1, 2],
    }
    cv = Canvas()
    PW, PH, PSTEP = 380, 74, 118
    lx = 330
    rx = lx + PW + 330
    top = 120
    cys = [top + i * PSTEP + PH / 2 for i in range(len(pk))]
    sys_l, sys_r = lx - 50, rx + PW - 330 + 50
    sys_r = lx + PW + 50
    sys_bottom = top + len(pk) * PSTEP + 10
    cv.rect(sys_l, 28, sys_r - sys_l, sys_bottom - 28)
    cv.text((sys_l + sys_r) / 2, 54, "Hệ thống Rentify", FS_TITLE, bold=True)
    for i, name in enumerate(pk):
        y = top + i * PSTEP
        cv.rect(lx, y, PW, PH)
        tw = text_w(name, FS_SMALL, True) + 28
        cv.rect(lx, y - TAB_H, tw, TAB_H)
        cv.text(lx + tw / 2, y - TAB_H / 2, name, FS_SMALL, bold=True)
        cv.text(lx + PW / 2, y + PH / 2, "\n".join(wrap(summary[i], PW - 40, FS_SMALL)), FS_SMALL)
    mid = (28 + sys_bottom) / 2
    actors = {
        "guest": ("Khách\nvãng lai", 120, (cys[0] + cys[3]) / 2 - 40, "L"),
        "tenant": ("Người\nthuê trọ", 120, cys[7], "L"),
        "landlord": ("Chủ trọ", sys_r + 190, cys[6], "R"),
        "admin": ("Quản trị viên", sys_r + 190, cys[1] - 20, "R"),
    }
    per_pkg = {}
    for a, idxs in links.items():
        for i in idxs:
            per_pkg.setdefault((i, actors[a][3]), []).append(a)
    order = ["guest", "tenant", "landlord", "admin"]
    for a, idxs in links.items():
        label, ax, ay, side = actors[a]
        origin = (ax + 26, ay - 12) if side == "L" else (ax - 26, ay - 12)
        for i in idxs:
            group = sorted(per_pkg[(i, side)], key=order.index)
            k = group.index(a)
            off = (k - (len(group) - 1) / 2) * 16
            x = lx if side == "L" else lx + PW
            cv.line(origin, (x, cys[i] + off))
    for a, (label, ax, ay, side) in actors.items():
        cv.stickman(ax, ay, label)
    cv.save(filename)


GUEST = [
    {
        "title": "Khám phá phòng trọ",
        "bases": [
            ("g1", "Tìm kiếm phòng trọ", 0),
            ("g3", "Tìm kiếm tòa nhà", 1),
            ("g2", "Xem chi tiết phòng", 2),
            ("g4", "Xem chi tiết tòa nhà", 3),
        ],
        "rel": [("g8", "Chọn khu vực", 0.5)],
        "links": [("g1", "g8", "include"), ("g3", "g8", "include")],
    },
    {
        "title": "Tài khoản và xác thực",
        "bases": [
            ("g5", "Đăng ký tài khoản", 0),
            ("g6", "Đăng nhập", 1),
            ("g7", "Quên mật khẩu", 2),
        ],
        "rel": [
            ("g9", "Xác thực email", 0),
            ("g10", "Gửi lại email xác thực", 1),
            ("g11", "Đặt lại mật khẩu", 2),
        ],
        "links": [("g5", "g9", "include"), ("g5", "g10", "extend"), ("g7", "g11", "include")],
    },
]

TENANT = [
    {
        "title": "Tài khoản",
        "bases": [("t1", "Đăng nhập, đăng xuất", 0), ("t2", "Quản lý hồ sơ cá nhân", 1)],
        "rel": [("t2a", "Đổi mật khẩu", 1)],
        "links": [("t2", "t2a", "extend")],
    },
    {
        "title": "Tìm phòng",
        "bases": [("t3", "Tìm phòng và lưu phòng yêu thích", 0)],
        "rel": [("t3a", "Tìm kiếm phòng trọ", 0)],
        "links": [("t3", "t3a", "include")],
    },
    {
        "title": "Hợp đồng và hóa đơn",
        "bases": [
            ("t4", "Xem phòng đang thuê", 0),
            ("t5", "Xem hợp đồng", 1),
            ("t6", "Xem hóa đơn và tiền điện nước", 2),
            ("t7", "Thanh toán hóa đơn bằng QR", 3),
            ("t8", "Xem lịch sử thanh toán", 4),
        ],
        "rel": [("t7a", "Xem chi tiết hóa đơn", 3)],
        "links": [("t7", "t7a", "include")],
    },
    {
        "title": "Sự cố",
        "bases": [("t9", "Báo cáo sự cố", 0), ("t10", "Theo dõi và hủy sự cố", 1)],
        "rel": [("t9a", "Đính kèm ảnh", 0)],
        "links": [("t9", "t9a", "extend")],
    },
    {
        "title": "Trò chuyện và thông báo",
        "bases": [("t11", "Trò chuyện", 0), ("t12", "Nhận và quản lý thông báo", 2)],
        "rel": [
            ("t11a", "Đính kèm tệp", 0),
            ("t11b", "Tìm tin nhắn", 1),
            ("t12a", "Đăng ký thiết bị nhận thông báo đẩy", 2),
        ],
        "links": [("t11", "t11a", "extend"), ("t11", "t11b", "extend"), ("t12", "t12a", "include")],
    },
    {
        "title": "Tìm bạn ở ghép",
        "bases": [("t13", "Quản lý hồ sơ ở ghép", 0), ("t14", "Tìm bạn và gửi yêu cầu ghép", 1)],
        "rel": [
            ("t14a", "Tìm hồ sơ ở ghép", 1),
            ("t14b", "Phản hồi yêu cầu ghép", 2),
        ],
        "links": [("t14", "t14a", "include"), ("t14", "t14b", "extend")],
    },
]

LANDLORD = [
    {
        "title": "Tài khoản",
        "bases": [("l1", "Đăng nhập và quản lý hồ sơ", 0)],
        "rel": [],
        "links": [],
    },
    {
        "title": "Tòa nhà và phòng",
        "bases": [("l2", "Quản lý tòa nhà", 0), ("l5", "Quản lý phòng", 1)],
        "rel": [("l2a", "Tải ảnh minh chứng sở hữu", 0), ("l5a", "Đánh dấu phòng sẵn sàng", 1)],
        "links": [("l2", "l2a", "include"), ("l5", "l5a", "extend")],
    },
    {
        "title": "Biểu giá và kỳ hóa đơn",
        "bases": [("l3", "Thiết lập biểu giá", 0), ("l4", "Cấu hình kỳ lập hóa đơn", 1)],
        "rel": [],
        "links": [],
    },
    {
        "title": "Hợp đồng",
        "bases": [
            ("l6", "Lập hợp đồng", 0),
            ("l7", "Kích hoạt hợp đồng", 2),
            ("l8", "Quản lý người thuê và thành viên", 3),
            ("l9", "Xử lý trả phòng và hợp đồng bị khóa", 4),
        ],
        "rel": [
            ("l6a", "Chọn mẫu hợp đồng", 0),
            ("l6b", "Sinh bản nháp PDF", 1),
            ("l7a", "Tải hợp đồng đã ký", 2),
        ],
        "links": [("l6", "l6a", "include"), ("l6", "l6b", "include"), ("l7", "l7a", "include")],
    },
    {
        "title": "Điện nước, hóa đơn, thanh toán",
        "bases": [
            ("l10", "Ghi chỉ số điện nước", 0),
            ("l11", "Lập và phát hành hóa đơn", 1),
            ("l12", "Ghi nhận thanh toán tiền mặt", 3),
            ("l13", "Đối soát giao dịch thanh toán", 4),
        ],
        "rel": [
            ("l10a", "Đính kèm ảnh bằng chứng", 0),
            ("l11a", "Chỉnh sửa hóa đơn", 1),
            ("l11b", "Hủy hóa đơn", 2),
        ],
        "links": [("l10", "l10a", "extend"), ("l11", "l11a", "extend"), ("l11", "l11b", "extend")],
    },
    {
        "title": "Sự cố",
        "bases": [("l14", "Xử lý sự cố", 0)],
        "rel": [],
        "links": [],
    },
    {
        "title": "Trò chuyện và thông báo",
        "bases": [("l15", "Trò chuyện với người thuê", 0), ("l16", "Nhận và quản lý thông báo", 1)],
        "rel": [("l15a", "Gửi nhắc nhở tự động", 0), ("l16a", "Đăng ký thiết bị nhận thông báo đẩy", 1)],
        "links": [("l15", "l15a", "extend"), ("l16", "l16a", "include")],
    },
]

ADMIN = [
    {
        "title": "Tài khoản",
        "bases": [("a1", "Đăng nhập và đổi mật khẩu", 0)],
        "rel": [],
        "links": [],
    },
    {
        "title": "Phê duyệt bất động sản",
        "bases": [("a2", "Duyệt bất động sản", 0)],
        "rel": [
            ("a2a", "Xem hàng đợi và chi tiết", 0),
            ("a2b", "Phê duyệt", 1),
            ("a2c", "Từ chối", 2),
        ],
        "links": [("a2", "a2a", "include"), ("a2", "a2b", "extend"), ("a2", "a2c", "extend")],
    },
    {
        "title": "Quản trị hệ thống",
        "bases": [
            ("a3", "Quản lý tài khoản", 0),
            ("a4", "Xem nhật ký kiểm toán", 2),
            ("a5", "Xem thống kê hệ thống", 3),
        ],
        "rel": [("a3a", "Khóa, mở khóa tài khoản", 0), ("a3b", "Xóa mềm tài khoản", 1)],
        "links": [("a3", "a3a", "extend"), ("a3", "a3b", "extend")],
    },
    {
        "title": "Thông báo",
        "bases": [("a6", "Nhận thông báo hệ thống", 0)],
        "rel": [],
        "links": [],
    },
]

if __name__ == "__main__":
    general_diagram("P8-10d-uc-general")
    actor_diagram("admin", "Hệ thống Rentify", "Quản trị viên", ADMIN, "P8-10d-uc-admin")
    actor_diagram("landlord", "Hệ thống Rentify", "Chủ trọ", LANDLORD, "P8-10d-uc-landlord")
    actor_diagram("tenant", "Hệ thống Rentify", "Người\nthuê trọ", TENANT, "P8-10d-uc-tenant")
    actor_diagram("guest", "Hệ thống Rentify", "Khách\nvãng lai", GUEST, "P8-10d-uc-guest")
    print("done")
