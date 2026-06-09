# HEARTBEAT.md

Keep this file empty (or with only comments) to skip heartbeat checks.

Add tasks below when you want periodic checks on Agor resources.

---

## Monthly Tasks

### 1st of Each Month — AWS COGS Report

1. Call `mcp__Birds__get_aws_billing` with:
   - `environment: "production"` (must specify — default is staging)
   - `start_date`: first day of previous month (e.g. on June 1 → `2026-05-01`)
   - `end_date`: first day of current month (e.g. `2026-06-01`)
   - `granularity: "MONTHLY"`
   - `group_by: ["SERVICE"]`

2. Format as CSV with these columns in order:
   `Service, Relational Database Service($), Savings Plans for Compute usage($), EC2-Instances($), EC2-Other($), ElastiCache($), Support (Business)($), CloudWatch($), MQ($), GuardDuty($), Backup($), S3($), Elastic Load Balancing($), Elastic Container Service for Kubernetes($), WAF($), VPC($), CloudTrail($), Key Management Service($), Lambda($), Route 53($), Secrets Manager($), Cost Explorer($), CloudWatch Events($), Elastic File System($), Kinesis Firehose($), SNS($), CloudShell($), Glue($), SQS($), Tax($), [Vanta($) if present], Total costs($)`

   Include two data rows: one labelled `Service total` and one labelled `YYYY-MM-01`.

   API → CSV column mappings:
   - "Amazon Relational Database Service" → Relational Database Service($)
   - "Savings Plans for AWS Compute usage" → Savings Plans for Compute usage($)
   - "Amazon Elastic Compute Cloud - Compute" → EC2-Instances($)
   - "EC2 - Other" → EC2-Other($)
   - "Amazon ElastiCache" → ElastiCache($)
   - "AWS Support (Business)" → Support (Business)($)
   - "AmazonCloudWatch" → CloudWatch($)
   - "Amazon MQ" → MQ($)
   - "Amazon GuardDuty" → GuardDuty($)
   - "AWS Backup" → Backup($)
   - "Amazon Simple Storage Service" → S3($)
   - "Amazon Elastic Load Balancing" → Elastic Load Balancing($)
   - "Amazon Elastic Container Service for Kubernetes" → Elastic Container Service for Kubernetes($)
   - "AWS WAF" → WAF($)
   - "Amazon Virtual Private Cloud" → VPC($)
   - "AWS CloudTrail" → CloudTrail($)
   - "AWS Key Management Service" → Key Management Service($)
   - "AWS Lambda" → Lambda($)
   - "Amazon Route 53" → Route 53($)
   - "AWS Secrets Manager" → Secrets Manager($)
   - "AWS Cost Explorer" → Cost Explorer($)
   - "CloudWatch Events" → CloudWatch Events($)
   - "Amazon Elastic File System" → Elastic File System($)
   - "Amazon Kinesis Firehose" → Kinesis Firehose($)
   - "Amazon Simple Notification Service" → SNS($)
   - "AWS CloudShell" → CloudShell($)
   - "AWS Glue" → Glue($)
   - "Amazon Simple Queue Service" → SQS($)
   - "Tax" → Tax($)
   - "Vanta" → Vanta($) (add as extra column between Tax and Total when present)

3. Send to Slack channel `C08UB8KBKD1` (`#aircfo-preset`) via `mcp__Slack__slack_send_message` as a code block. Note any anomalies (e.g. a service showing $0 unexpectedly, or a large one-time charge like Vanta).

---

## Agor Resource Checks

### Active Worktrees
- Check for stale worktrees (no activity in >7 days)
- Identify worktrees with failed CI/CD
- Look for completed work that can be cleaned up

### Running Sessions
- Check for blocked/stuck sessions
- Review failed tasks needing attention
- Identify sessions waiting for callbacks

### Board Organization
- Review board zones and organization
- Move completed worktrees to archive zone
- Update worktree notes/metadata if stale

---

## Memory Maintenance

### Periodic Tasks
- Review recent daily logs (`memory/YYYY-MM-DD.md`)
- Update `MEMORY.md` with significant learnings
- Sync `memory/agor-state/` with current Agor state
- Commit workspace changes if modified

---

## Example Heartbeat Tasks

```markdown
## Daily Checks (if enabled)

- [ ] Sync Agor state: refresh worktrees.json and sessions.json
- [ ] Review yesterday's log, extract learnings to MEMORY.md
- [ ] Check for stuck/failed sessions on main board
- [ ] Commit workspace changes if any

## Weekly Checks (if enabled)

- [ ] Review all active worktrees, identify cleanup candidates
- [ ] Archive old daily logs (keep last 30 days)
- [ ] Review MEMORY.md, remove outdated information
- [ ] Update skills based on learnings
```

---

**Note:** Heartbeats are optional. Many agents work better in reactive mode (human-initiated). Use heartbeats if you need proactive monitoring of Agor resources.
