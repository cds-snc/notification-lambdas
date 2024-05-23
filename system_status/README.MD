# System Status Calculation

System Status Calculation is done based on 4 checks:

1. Admin URL response time
1. API URL response time
1. Emails sent for high/ medium/ low queues
1. SMSs sent for high/ medium/ low queues

For the purpose of this README, we will expand on Emails and SMSs sent through the queues. The Admin and API checks are pings against their respective URLs and ensuring the response occur within a certain threshold as set in our SLAs.

## Email and SMS Calculation

There are 6 heartbeat template_ids that exist in our DB. High/ medium/ low - each for email and for sms. We use those template_ids and different time frames to calculate whether our system is meeting our SLAs or not.

### Notification Statuses in our Database

We store the following notification statuses in our database.

NOTIFICATION_CANCELLED = "cancelled"  
NOTIFICATION_CREATED = "created"  
NOTIFICATION_SENDING = "sending"  
NOTIFICATION_SENT = "sent"  
NOTIFICATION_DELIVERED = "delivered"  
NOTIFICATION_PENDING = "pending"  
NOTIFICATION_FAILED = "failed"  
NOTIFICATION_TECHNICAL_FAILURE = "technical-failure"  
NOTIFICATION_TEMPORARY_FAILURE = "temporary-failure"  
NOTIFICATION_PERMANENT_FAILURE = "permanent-failure"

```
FAILURE_STATUSES = [NOTIFICATION_FAILED, NOTIFICATION_TECHNICAL_FAILURE, NOTIFICATION_TEMPORARY_FAILURE, NOTIFICATION_PERMANENT_FAILURE]

DELIVERY_STATUSES = [NOTIFICATION_DELIVERED, NOTIFICATION_SENDING, NOTIFICATION_SENT]

If NOTIFICATION_CREATED after a certain time, the system can be assumed to be slower than expected.

```
### High
Email and SMS that are in our high queues need to be delivered within 60 seconds.

Status calculation:

    Up: Any message that was created 60 seconds ago has to have a status in DELIVERY_STATUSES
    Down: Either NOTIFICATION_CREATED or FAILURE_STATUSES
    Degraded: If neither Up nor Down

### Medium and Low
For both Medium we look at two time periods:  
M1: Notifications created between [52, 47] minutes ago  
M2: Notifications created between [20, 15] minutes ago

For Low the two time periods are:  
L1: Notifications created between [3h 7min, 3h 2min] ago  
L2: Notifications created between [20, 15] minutes ago

The reason for these two groups is because if a notification failed in the (L/M)1 group, but the (L/M)2 group is delivering notifications - we can reasonably assume that the system was facing a failure some time ago, but it is currently not experiencing any issues

Status calculation:

    Up: (L/M)1 have DELIVERY STATUSES or (L/M)2 have DELIVERY_STATUSES
    Down: (L/M)1 has NOTIFICATION_CREATED/FAILURE_STATUSES AND (L/M)2 has NOTIFICATION_CREATED/FAILURE_STATUSES
    Degraded: If neither Up or Down
