# Ki?m k? operation OpenAPI

Ngu?n: `api-docs/reference/rentify.json` trong workspace t?i th?i ?i?m r? so?t; b?n bundle c? thay ??i ch?a commit v? c? th? kh?c YAML ngu?n. Danh s?ch n?y l? ch? m?c s?ng l?c, kh?ng ph?i x?c nh?n endpoint ho?t ??ng, FE t?ch h?p, hay ?? deploy. ?C? tr?ng t?n? ngh?a l? operationId xu?t hi?n trong controller c?a ba service; ?C?n ??i chi?u route? c? th? l? kh?c t?n, kh?ng ph?i b?ng ch?ng thi?u. C?c route n?i b? kh?ng thu?c contract n?y.

T?ng: 130 operation. Chi ti?t k?t lu?n v? issue xem [b?o c?o](audit.md).

| Method | Path | operationId | API status | D?u hi?u trong controller |
|---|---|---|---|---|
| GET | `/.well-known/jwks.json` | `getJwks` | released | C? tr?ng t?n |
| GET | `/admin/buildings` | `getAdminBuildings` | released | C? tr?ng t?n |
| GET | `/admin/buildings/{buildingId}` | `getAdminBuildingsBuildingid` | released | C? tr?ng t?n |
| GET | `/administrative-units/provinces` | `getAdministrativeProvinces` | released | C? tr?ng t?n |
| GET | `/administrative-units/provinces/{provinceCode}/wards` | `getAdministrativeWards` | released | C? tr?ng t?n |
| GET | `/audit-logs` | `getAuditLogs` | designing | C?n ??i chi?u route |
| GET | `/audit-logs/{auditLogId}` | `getAuditLogsAuditlogid` | designing | C?n ??i chi?u route |
| POST | `/auth/email-verification-requests` | `requestEmailVerification` | released | C? tr?ng t?n |
| POST | `/auth/email-verifications` | `verifyRegisteredEmail` | released | C? tr?ng t?n |
| POST | `/auth/login` | `loginAccount` | released | C? tr?ng t?n |
| POST | `/auth/logout` | `logoutSession` | released | C?n ??i chi?u route |
| POST | `/auth/password-reset-requests` | `requestPasswordReset` | released | C? tr?ng t?n |
| POST | `/auth/password-resets` | `resetPassword` | released | C? tr?ng t?n |
| POST | `/auth/refresh` | `refreshSession` | released | C?n ??i chi?u route |
| POST | `/auth/register` | `registerAccount` | released | C? tr?ng t?n |
| GET | `/billing-settings` | `getBillingSettings` | released | C? tr?ng t?n |
| POST | `/billing-settings` | `postBillingSettings` | released | C? tr?ng t?n |
| PATCH | `/billing-settings/{billingSettingId}` | `patchBillingSettingsBillingsettingid` | released | C? tr?ng t?n |
| GET | `/buildings` | `getBuildings` | released | C? tr?ng t?n |
| POST | `/buildings` | `postBuildings` | released | C? tr?ng t?n |
| DELETE | `/buildings/{buildingId}` | `deleteBuildingsBuildingid` | released | C? tr?ng t?n |
| GET | `/buildings/{buildingId}` | `getBuildingsBuildingid` | released | C? tr?ng t?n |
| PATCH | `/buildings/{buildingId}` | `patchBuildingsBuildingid` | released | C? tr?ng t?n |
| POST | `/buildings/{buildingId}/approve` | `postBuildingsBuildingidApprove` | released | C? tr?ng t?n |
| POST | `/buildings/{buildingId}/rate-policies/batch` | `postBuildingRatePoliciesBatch` | released | C? tr?ng t?n |
| POST | `/buildings/{buildingId}/reject` | `postBuildingsBuildingidReject` | released | C? tr?ng t?n |
| PUT | `/buildings/{buildingId}/vietqr-config` | `putBuildingVietQrConfig` | designing | C?n ??i chi?u route |
| GET | `/contract-members` | `getContractMembers` | released | C? tr?ng t?n |
| POST | `/contract-members` | `postContractMembers` | released | C? tr?ng t?n |
| PATCH | `/contract-members/{tenantId}` | `patchContractMembersTenantid` | released | C? tr?ng t?n |
| POST | `/contract-members/{tenantId}/leave-contract` | `postContractMembersTenantidLeaveContract` | released | C? tr?ng t?n |
| GET | `/contract-templates` | `getContractTemplates` | released | C? tr?ng t?n |
| GET | `/contract-templates/{templateKey}` | `getContractTemplatesTemplatekey` | released | C? tr?ng t?n |
| GET | `/contracts` | `getContracts` | released | C? tr?ng t?n |
| POST | `/contracts` | `postContracts` | released | C? tr?ng t?n |
| GET | `/contracts/{contractId}` | `getContractsContractid` | released | C? tr?ng t?n |
| PATCH | `/contracts/{contractId}` | `patchContractsContractid` | released | C? tr?ng t?n |
| POST | `/contracts/{contractId}/activate-contract` | `postContractsContractidActivateContract` | released | C? tr?ng t?n |
| PUT | `/contracts/{contractId}/apply-template` | `putContractsContractidApplyTemplate` | designing | C?n ??i chi?u route |
| POST | `/contracts/{contractId}/complete-checkout` | `postContractsContractidCompleteCheckout` | released | C? tr?ng t?n |
| POST | `/contracts/{contractId}/deposit-settlement` | `postContractDepositSettlement` | deprecated | C?n ??i chi?u route |
| POST | `/contracts/{contractId}/generate-draft-document` | `postContractsContractidGenerateDraftDocument` | designing | C?n ??i chi?u route |
| GET | `/conversations` | `getConversations` | released | C? tr?ng t?n |
| POST | `/conversations` | `createConversation` | released | C? tr?ng t?n |
| GET | `/conversations/unread-summary` | `getConversationsUnreadSummary` | released | C? tr?ng t?n |
| GET | `/conversations/{conversationId}` | `getConversationsConversationid` | released | C? tr?ng t?n |
| PATCH | `/conversations/{conversationId}` | `updateConversation` | released | C? tr?ng t?n |
| POST | `/conversations/{conversationId}/bot-reminders` | `sendBotReminder` | designing | C?n ??i chi?u route |
| GET | `/conversations/{conversationId}/members` | `listConversationMembers` | released | C? tr?ng t?n |
| POST | `/conversations/{conversationId}/members` | `addConversationMembers` | released | C? tr?ng t?n |
| DELETE | `/conversations/{conversationId}/members/me` | `leaveConversation` | released | C? tr?ng t?n |
| DELETE | `/conversations/{conversationId}/members/{userId}` | `removeConversationMember` | released | C? tr?ng t?n |
| PUT | `/conversations/{conversationId}/members/{userId}/role` | `updateConversationMemberRole` | released | C? tr?ng t?n |
| GET | `/dashboard` | `getDashboard` | designing | C?n ??i chi?u route |
| GET | `/invoices` | `getInvoices` | developing | C? tr?ng t?n |
| POST | `/invoices/generate` | `postInvoicesGenerate` | developing | C? tr?ng t?n |
| POST | `/invoices/issue-invoice` | `postInvoicesIssueInvoice` | developing | C? tr?ng t?n |
| GET | `/invoices/{invoiceId}` | `getInvoicesInvoiceid` | developing | C? tr?ng t?n |
| PATCH | `/invoices/{invoiceId}` | `patchInvoicesInvoiceid` | developing | C? tr?ng t?n |
| POST | `/invoices/{invoiceId}/cancel-invoice` | `postInvoicesInvoiceidCancelInvoice` | developing | C? tr?ng t?n |
| GET | `/issues` | `getIssues` | designing | C?n ??i chi?u route |
| POST | `/issues` | `postIssues` | designing | C?n ??i chi?u route |
| GET | `/issues/{issueId}` | `getIssuesIssueid` | designing | C?n ??i chi?u route |
| PATCH | `/issues/{issueId}` | `patchIssuesIssueid` | designing | C?n ??i chi?u route |
| POST | `/issues/{issueId}/cancel` | `postIssuesIssueidCancel` | designing | C?n ??i chi?u route |
| GET | `/match-requests` | `getMatchRequests` | designing | C?n ??i chi?u route |
| POST | `/match-requests` | `postMatchRequests` | designing | C?n ??i chi?u route |
| POST | `/match-requests/{matchRequestId}/accept-request` | `postMatchRequestsMatchrequestidAcceptRequest` | designing | C?n ??i chi?u route |
| POST | `/match-requests/{matchRequestId}/reject-request` | `postMatchRequestsMatchrequestidRejectRequest` | designing | C?n ??i chi?u route |
| POST | `/match-requests/{matchRequestId}/withdraw-request` | `postMatchRequestsMatchrequestidWithdrawRequest` | designing | C?n ??i chi?u route |
| GET | `/me` | `getCurrentUser` | released | C? tr?ng t?n |
| PATCH | `/me` | `updateCurrentUser` | released | C? tr?ng t?n |
| GET | `/me/buildings` | `getMeBuildings` | released | C? tr?ng t?n |
| GET | `/me/buildings/{buildingId}` | `getMeBuildingsBuildingid` | released | C? tr?ng t?n |
| GET | `/me/contracts` | `getMeContracts` | released | C? tr?ng t?n |
| GET | `/me/favorite-rooms` | `getMeFavoriteRooms` | designing | C?n ??i chi?u route |
| POST | `/me/favorite-rooms` | `postMeFavoriteRooms` | designing | C?n ??i chi?u route |
| DELETE | `/me/favorite-rooms/{roomId}` | `deleteMeFavoriteRoomsRoomid` | designing | C?n ??i chi?u route |
| GET | `/me/invoices` | `getMeInvoices` | developing | C? tr?ng t?n |
| GET | `/me/issues` | `getMeIssues` | designing | C?n ??i chi?u route |
| GET | `/me/notification-preference` | `getMeNotificationPreference` | released | C? tr?ng t?n |
| PUT | `/me/notification-preference` | `putMeNotificationPreference` | released | C? tr?ng t?n |
| PUT | `/me/password` | `changeCurrentUserPassword` | released | C? tr?ng t?n |
| GET | `/me/payments` | `getMePayments` | deprecated | C?n ??i chi?u route |
| POST | `/me/push-devices` | `postMePushDevices` | released | C? tr?ng t?n |
| DELETE | `/me/push-devices/{deviceId}` | `deleteMePushDevicesDeviceid` | released | C? tr?ng t?n |
| GET | `/me/room-hub` | `getMeRoomHub` | designing | C?n ??i chi?u route |
| GET | `/me/roommate-profile` | `getMeRoommateProfile` | designing | C?n ??i chi?u route |
| PUT | `/me/roommate-profile` | `putMeRoommateProfile` | designing | C?n ??i chi?u route |
| GET | `/me/rooms` | `getMeRooms` | released | C? tr?ng t?n |
| POST | `/media/presign-upload` | `postMediaPresignUpload` | released | C? tr?ng t?n |
| DELETE | `/media/{mediaId}` | `deleteMediaMediaid` | released | C? tr?ng t?n |
| GET | `/media/{mediaId}` | `getMediaMediaid` | released | C? tr?ng t?n |
| POST | `/media/{mediaId}/complete-upload` | `postMediaMediaidCompleteUpload` | released | C? tr?ng t?n |
| GET | `/media/{mediaId}/download-url` | `getMediaDownloadUrl` | released | C? tr?ng t?n |
| GET | `/messages` | `getMessages` | released | C? tr?ng t?n |
| POST | `/messages` | `postMessages` | released | C? tr?ng t?n |
| POST | `/messages/mark-read` | `postMessagesMarkRead` | released | C? tr?ng t?n |
| GET | `/messages/search` | `getMessagesSearch` | designing | C? tr?ng t?n |
| GET | `/meter-readings` | `getMeterReadings` | released | C? tr?ng t?n |
| POST | `/meter-readings` | `postMeterReadings` | released | C? tr?ng t?n |
| POST | `/meter-readings/bulk` | `postBulkMeterReadings` | released | C? tr?ng t?n |
| PATCH | `/meter-readings/{meterReadingId}` | `patchMeterReading` | developing | C? tr?ng t?n |
| PATCH | `/meter-readings/{readingId}/evidence` | `patchMeterReadingEvidence` | developing | C? tr?ng t?n |
| GET | `/notifications` | `getNotifications` | released | C? tr?ng t?n |
| POST | `/notifications/mark-all-read` | `postNotificationsMarkAllRead` | released | C? tr?ng t?n |
| POST | `/notifications/{notificationId}/mark-read` | `postNotificationsNotificationidMarkRead` | released | C? tr?ng t?n |
| GET | `/payments` | `getPayments` | deprecated | C?n ??i chi?u route |
| POST | `/payments/create-intent` | `postPaymentsCreateIntent` | deprecated | C?n ??i chi?u route |
| POST | `/payments/record-cash-payment` | `postPaymentsRecordCashPayment` | deprecated | C?n ??i chi?u route |
| POST | `/payments/webhooks/{provider}` | `postPaymentsWebhooksProvider` | deprecated | C?n ??i chi?u route |
| GET | `/rate-policies` | `getRatePolicies` | released | C? tr?ng t?n |
| POST | `/rate-policies` | `postRatePolicies` | released | C? tr?ng t?n |
| PATCH | `/rate-policies/{ratePolicyId}` | `patchRatePoliciesRatepolicyid` | released | C? tr?ng t?n |
| POST | `/rate-policies/{ratePolicyId}/deactivate-policy` | `postRatePoliciesRatepolicyidDeactivatePolicy` | released | C? tr?ng t?n |
| GET | `/roommate-profiles` | `getRoommateProfiles` | designing | C?n ??i chi?u route |
| GET | `/roommate-profiles/{roommateProfileId}` | `getRoommateProfilesRoommateprofileid` | designing | C?n ??i chi?u route |
| GET | `/rooms` | `getRooms` | released | C? tr?ng t?n |
| POST | `/rooms` | `postRooms` | released | C? tr?ng t?n |
| DELETE | `/rooms/{roomId}` | `deleteRoomsRoomid` | released | C? tr?ng t?n |
| GET | `/rooms/{roomId}` | `getRoomsRoomid` | released | C? tr?ng t?n |
| PATCH | `/rooms/{roomId}` | `patchRoomsRoomid` | released | C? tr?ng t?n |
| POST | `/rooms/{roomId}/mark-ready` | `postRoomsRoomidMarkReady` | released | C? tr?ng t?n |
| GET | `/users` | `getUsersAdmin` | released | C? tr?ng t?n |
| GET | `/users/directory` | `getUsersDirectory` | released | C? tr?ng t?n |
| DELETE | `/users/{userId}` | `deleteUserById` | released | C?n ??i chi?u route |
| GET | `/users/{userId}` | `getUserById` | released | C?n ??i chi?u route |
| PATCH | `/users/{userId}` | `updateUserById` | released | C?n ??i chi?u route |
| POST | `/users/{userId}/lock` | `lockUser` | released | C? tr?ng t?n |
| POST | `/users/{userId}/unlock` | `unlockUser` | released | C? tr?ng t?n |
