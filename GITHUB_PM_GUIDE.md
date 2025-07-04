# GitHub Project Management Guide

## 🚀 Your Project Management Workflow

### Quick Commands

```bash
# View your issues
gh issue list

# Create new issues
gh issue create --template bug_report
gh issue create --template feature_request
gh issue create --template user_story

# View milestones
gh api repos/GuillaumeRacine/Transcripts_MVP/milestones

# Assign issues
gh issue edit 1 --assignee "@me"
gh issue edit 1 --add-label "priority:high"

# Close completed issues
gh issue close 1
```

### 📋 Daily Workflow

1. **Morning Planning**
   ```bash
   gh issue list --assignee "@me" --state open
   ```

2. **Create New Work**
   ```bash
   gh issue create --title "Add bulk import feature" --label "enhancement,priority:medium"
   ```

3. **Update Progress**
   ```bash
   gh issue edit 1 --add-label "status:in-progress"
   ```

4. **Complete Work**
   ```bash
   gh issue close 1 --comment "Completed in PR #5"
   ```

### 🎯 Sprint Planning

#### 1. Create Sprint Milestone
```bash
gh api repos/GuillaumeRacine/Transcripts_MVP/milestones --method POST --field title="Sprint 1" --field description="Two week sprint focusing on database improvements"
```

#### 2. Add Issues to Sprint
```bash
gh issue edit 1 --milestone "Sprint 1"
gh issue edit 2 --milestone "Sprint 1"
```

#### 3. Track Sprint Progress
```bash
gh issue list --milestone "Sprint 1"
```

### 📊 Release Management

#### 1. Plan Release
```bash
# Tag issues for release
gh issue edit 1 --add-label "release:v1.1"
gh issue edit 2 --add-label "release:v1.1"
```

#### 2. Create Release
```bash
gh release create v1.1.0 --title "Database Workflow Release" --notes "Complete Notion database integration"
```

#### 3. Track Release Progress
```bash
gh issue list --label "release:v1.1" --state open
```

### 🏷️ Label Usage Guide

#### Priority Labels
- `priority:critical` - Blocking core functionality
- `priority:high` - Important for next release
- `priority:medium` - Normal development priority
- `priority:low` - Nice to have features

#### Status Labels
- `status:blocked` - Waiting on external dependency
- `status:in-progress` - Currently being worked on
- `status:needs-review` - Ready for code review
- `status:testing` - Ready for QA testing

#### Component Labels
- `component:frontend` - UI/UX changes
- `component:backend` - Server logic
- `component:ai-llm` - AI processing
- `component:youtube-api` - YouTube integration
- `component:notion-api` - Notion integration

#### Size Labels (Story Points)
- `size:xs` - 1 point (quick fix)
- `size:small` - 2-3 points (few hours)
- `size:medium` - 5-8 points (1-2 days)
- `size:large` - 13+ points (multiple days)

### 📈 Reporting & Analytics

#### 1. Burndown Tracking
```bash
# Issues remaining in milestone
gh issue list --milestone "Sprint 1" --state open

# Completed this week
gh issue list --milestone "Sprint 1" --state closed
```

#### 2. Component Analysis
```bash
# Issues by component
gh issue list --label "component:frontend"
gh issue list --label "component:backend"
```

#### 3. Priority Distribution
```bash
gh issue list --label "priority:high" --state open
gh issue list --label "priority:medium" --state open
```

### 🔄 Automation Examples

#### 1. Daily Standup Prep
```bash
#!/bin/bash
echo "🏃‍♂️ Daily Standup - $(date)"
echo "=========================="
echo "📋 My Open Issues:"
gh issue list --assignee "@me" --state open --json number,title,labels

echo -e "\n📈 In Progress:"
gh issue list --label "status:in-progress" --state open

echo -e "\n🚫 Blocked Issues:"
gh issue list --label "status:blocked" --state open
```

#### 2. Sprint Summary
```bash
#!/bin/bash
SPRINT="Sprint 1"
echo "📊 Sprint Summary: $SPRINT"
echo "=========================="
echo "✅ Completed:"
gh issue list --milestone "$SPRINT" --state closed --json number,title

echo -e "\n📋 Remaining:"
gh issue list --milestone "$SPRINT" --state open --json number,title
```

#### 3. Release Readiness Check
```bash
#!/bin/bash
RELEASE="release:v1.1"
echo "🚀 Release Readiness: $RELEASE"
echo "=========================="
echo "❌ Blocking Issues:"
gh issue list --label "$RELEASE" --label "priority:critical" --state open

echo -e "\n⚠️ High Priority:"
gh issue list --label "$RELEASE" --label "priority:high" --state open

echo -e "\n✅ Ready to Ship:"
gh issue list --label "$RELEASE" --state closed --json number,title
```

### 🎯 Best Practices

1. **Issue Naming**
   - Use action verbs: "Add", "Fix", "Update", "Remove"
   - Be specific: "Add CSV import for bulk video processing"
   - Include context: "Fix rate limiting error in YouTube API"

2. **Label Hygiene**
   - Always add priority and component labels
   - Update status labels as work progresses
   - Use size labels for planning and estimation

3. **Milestone Management**
   - Keep milestones focused (2-4 weeks max)
   - Review and adjust scope regularly
   - Close completed milestones promptly

4. **Epic Tracking**
   - Break large features into smaller issues
   - Reference epic numbers in related issues
   - Update epic descriptions with progress

### 🔗 Useful Links

- **Issues**: https://github.com/GuillaumeRacine/Transcripts_MVP/issues
- **Milestones**: https://github.com/GuillaumeRacine/Transcripts_MVP/milestones
- **Labels**: https://github.com/GuillaumeRacine/Transcripts_MVP/labels
- **Projects**: https://github.com/GuillaumeRacine/Transcripts_MVP/projects