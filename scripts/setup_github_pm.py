#!/usr/bin/env python3
"""
Setup GitHub Project Management for Transcripts MVP
"""
import subprocess
import json
import sys

def run_gh_command(cmd, description=""):
    """Run GitHub CLI command with error handling"""
    print(f"🔄 {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success: {description}")
        return result.stdout.strip()
    else:
        print(f"⚠️ {description}: {result.stderr.strip()}")
        return None

def setup_labels():
    """Create standard product management labels"""
    print("\n📋 Setting up product management labels...")
    
    labels = [
        # Epic and Story labels
        ("epic", "purple", "Large feature or capability requiring multiple sprints"),
        ("user-story", "0E7DB8", "User-facing functionality or requirement"),
        ("technical-debt", "B60205", "Code improvement that doesn't add features"),
        
        # Bug and Issue types
        ("bug", "D73A4A", "Something isn't working as expected"),
        ("enhancement", "A2EEEF", "New feature or improvement request"),
        ("documentation", "0075CA", "Improvements or additions to documentation"),
        
        # Priority levels
        ("priority:critical", "B60205", "Critical issue blocking core functionality"),
        ("priority:high", "D93F0B", "High priority - should be addressed soon"),
        ("priority:medium", "FBCA04", "Medium priority - normal timeline"),
        ("priority:low", "0E8A16", "Low priority - nice to have"),
        
        # Status labels
        ("status:blocked", "000000", "Work is blocked by external dependency"),
        ("status:in-progress", "C2E0C6", "Currently being worked on"),
        ("status:needs-review", "D876E3", "Ready for code review"),
        ("status:testing", "F9D0C4", "Ready for testing"),
        
        # Component labels
        ("component:frontend", "28A745", "Frontend UI/UX development"),
        ("component:backend", "6F42C1", "Backend API and server logic"),
        ("component:database", "E99695", "Database schema and operations"),
        ("component:ai-llm", "FF6B9D", "AI/LLM integration and processing"),
        ("component:youtube-api", "FF0000", "YouTube API integration"),
        ("component:notion-api", "000000", "Notion API integration"),
        
        # Size estimates (story points)
        ("size:xs", "E6F3FF", "Extra small - 1 point"),
        ("size:small", "B3E0FF", "Small - 2-3 points"),
        ("size:medium", "80CCFF", "Medium - 5-8 points"),
        ("size:large", "4DB8FF", "Large - 13+ points"),
        
        # Release labels
        ("release:v1.0", "FEF2C0", "Planned for v1.0 release"),
        ("release:v1.1", "F0E68C", "Planned for v1.1 release"),
        ("release:backlog", "D3D3D3", "Future release - not yet planned")
    ]
    
    for label_name, color, description in labels:
        cmd = f'gh label create "{label_name}" --color {color} --description "{description}"'
        run_gh_command(cmd, f"Creating label: {label_name}")

def setup_milestones():
    """Create product milestones"""
    print("\n🎯 Setting up product milestones...")
    
    milestones = [
        ("v1.0 - Core Features", "Stable release with essential YouTube transcript processing"),
        ("v1.1 - Database Workflow", "Complete Notion database integration with enhanced UX"),
        ("v1.2 - Advanced Features", "Bulk processing, advanced filters, and analytics"),
        ("v2.0 - Platform Expansion", "Multi-platform support and enterprise features")
    ]
    
    for title, description in milestones:
        # Create milestone using GitHub API
        milestone_data = {
            "title": title,
            "description": description,
            "state": "open"
        }
        
        cmd = f"gh api repos/GuillaumeRacine/Transcripts_MVP/milestones --method POST --input -"
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=json.dumps(milestone_data))
        
        if process.returncode == 0:
            print(f"✅ Created milestone: {title}")
        else:
            print(f"⚠️ Milestone creation: {stderr.strip()}")

def create_epic_issues():
    """Create epic issues for major features"""
    print("\n📚 Creating epic issues...")
    
    epics = [
        {
            "title": "Epic: Enhanced YouTube API Integration",
            "body": """## Overview
Improve YouTube API integration with better error handling, rate limiting, and service account management.

## Goals
- Robust service account authentication
- Intelligent rate limiting with backoff
- Better error messages and recovery
- Support for multiple video sources

## Success Metrics
- 99% successful API calls
- Zero rate limit violations
- User-friendly error messages
- Support for 1000+ videos per day

## User Stories
- [ ] Service account setup automation
- [ ] Rate limit status dashboard
- [ ] Automatic retry with exponential backoff
- [ ] Bulk video URL import
""",
            "labels": ["epic", "priority:high", "component:youtube-api", "release:v1.1"]
        },
        {
            "title": "Epic: Advanced Notion Database Features",
            "body": """## Overview
Enhance Notion database integration with advanced features and better user experience.

## Goals
- Bulk operations support
- Advanced filtering and search
- Custom summary templates
- Progress tracking and analytics

## Success Metrics
- Support for 100+ videos in single operation
- Custom summary formats
- Real-time progress tracking
- User satisfaction score > 8/10

## User Stories
- [ ] Bulk video import from CSV
- [ ] Custom summary templates
- [ ] Progress tracking dashboard
- [ ] Advanced filtering options
- [ ] Export capabilities
""",
            "labels": ["epic", "priority:medium", "component:notion-api", "release:v1.2"]
        },
        {
            "title": "Epic: AI/LLM Processing Improvements",
            "body": """## Overview
Enhance AI processing capabilities with better prompts, multiple providers, and advanced features.

## Goals
- Support multiple LLM providers
- Custom prompt templates
- Summary quality improvements
- Cost optimization

## Success Metrics
- Support for 3+ LLM providers
- 50% improvement in summary quality
- 30% reduction in processing costs
- Custom prompt satisfaction > 9/10

## User Stories
- [ ] Multi-provider LLM support
- [ ] Custom prompt templates
- [ ] Summary quality scoring
- [ ] Cost tracking and optimization
- [ ] A/B testing for prompts
""",
            "labels": ["epic", "priority:medium", "component:ai-llm", "release:v1.2"]
        }
    ]
    
    for epic in epics:
        labels_str = " ".join([f'--label "{label}"' for label in epic["labels"]])
        cmd = f'gh issue create --title "{epic["title"]}" --body "{epic["body"]}" {labels_str}'
        run_gh_command(cmd, f"Creating epic: {epic['title']}")

def create_user_stories():
    """Create specific user story issues"""
    print("\n👤 Creating user story issues...")
    
    stories = [
        {
            "title": "User can import multiple video URLs from CSV file",
            "body": """## User Story
As a content manager, I want to upload a CSV file with multiple YouTube URLs so that I can process large batches of videos efficiently.

## Acceptance Criteria
- [ ] User can upload CSV file through web interface
- [ ] System validates all URLs before processing
- [ ] Batch processing with progress tracking
- [ ] Error reporting for invalid URLs
- [ ] Support for 100+ URLs per batch

## Definition of Done
- [ ] CSV upload functionality implemented
- [ ] URL validation with clear error messages
- [ ] Progress tracking visible in Notion
- [ ] Error handling and recovery
- [ ] Documentation updated
""",
            "labels": ["user-story", "enhancement", "priority:high", "component:frontend", "size:large"]
        },
        {
            "title": "User can customize AI summary templates",
            "body": """## User Story
As a user, I want to create custom summary templates so that I can get summaries tailored to my specific needs and use cases.

## Acceptance Criteria
- [ ] Template editor with preview functionality
- [ ] Save and reuse custom templates
- [ ] Variable substitution (title, channel, etc.)
- [ ] Template sharing capabilities
- [ ] Default templates for common use cases

## Definition of Done
- [ ] Template editor UI implemented
- [ ] Template storage and management
- [ ] Preview functionality working
- [ ] Variable substitution system
- [ ] Documentation and examples provided
""",
            "labels": ["user-story", "enhancement", "priority:medium", "component:ai-llm", "size:medium"]
        },
        {
            "title": "User can view processing progress in real-time",
            "body": """## User Story
As a user, I want to see real-time progress of video processing so that I can track status and estimate completion time.

## Acceptance Criteria
- [ ] Real-time status updates in Notion database
- [ ] Progress percentage for long-running operations
- [ ] Estimated time remaining
- [ ] Error notifications with details
- [ ] Ability to cancel long-running operations

## Definition of Done
- [ ] Real-time status system implemented
- [ ] Progress tracking with percentages
- [ ] Time estimation algorithm
- [ ] Notification system for errors
- [ ] Cancel operation functionality
""",
            "labels": ["user-story", "enhancement", "priority:medium", "component:backend", "size:medium"]
        }
    ]
    
    for story in stories:
        labels_str = " ".join([f'--label "{label}"' for label in story["labels"]])
        cmd = f'gh issue create --title "{story["title"]}" --body "{story["body"]}" {labels_str}'
        run_gh_command(cmd, f"Creating user story: {story['title']}")

def create_project_board():
    """Create project board for tracking work"""
    print("\n📊 Creating project board...")
    
    # Create project using new GitHub Projects (Projects v2)
    cmd = 'gh project create --title "Transcripts MVP Roadmap" --body "Track development progress, features, and releases for the YouTube Transcripts to Notion MVP"'
    result = run_gh_command(cmd, "Creating project board")
    
    if result:
        print("✅ Project board created successfully!")
        print("📋 Next: Add issues to your project board manually in GitHub")

def setup_issue_templates():
    """Create issue templates for consistent reporting"""
    print("\n📝 Setting up issue templates...")
    
    # Create .github directory if it doesn't exist
    import os
    os.makedirs(".github/ISSUE_TEMPLATE", exist_ok=True)
    
    # Bug report template
    bug_template = """---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug, needs-triage'
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Environment
- OS: [e.g. macOS, Windows, Linux]
- Python Version: [e.g. 3.9]
- Browser: [e.g. chrome, safari]
- Version: [e.g. 22]

## Additional Context
Add any other context about the problem here.

## Impact
- [ ] Critical (Blocks core functionality)
- [ ] High (Major feature unusable)
- [ ] Medium (Minor feature issue)
- [ ] Low (Cosmetic issue)
"""
    
    # Feature request template
    feature_template = """---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement, needs-triage'
assignees: ''
---

## Feature Request Summary
A clear and concise description of what the problem is or what you'd like to see added.

## Proposed Solution
A clear and concise description of what you want to happen.

## User Story
As a [type of user], I want [goal] so that [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Alternatives Considered
A clear and concise description of any alternative solutions or features you've considered.

## Additional Context
Add any other context, mockups, or screenshots about the feature request here.

## Priority
- [ ] Must Have (P0)
- [ ] Should Have (P1)
- [ ] Could Have (P2)
- [ ] Won't Have This Time (P3)

## Success Metrics
How will we measure the success of this feature?
"""
    
    # User story template
    story_template = """---
name: User Story
about: Create a user story for new functionality
title: '[STORY] User can...'
labels: 'user-story, needs-estimation'
assignees: ''
---

## User Story
As a [type of user], I want [goal] so that [benefit].

## Acceptance Criteria
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

## Definition of Done
- [ ] Code implemented and tested
- [ ] UI/UX reviewed and approved
- [ ] Documentation updated
- [ ] Stakeholder acceptance received
- [ ] No breaking changes to existing functionality

## Story Points Estimate
- [ ] XS (1 point)
- [ ] Small (2-3 points)
- [ ] Medium (5-8 points)
- [ ] Large (13+ points)

## Dependencies
List any dependencies or blockers for this story.

## Notes
Additional context, mockups, or technical notes.
"""
    
    # Write templates to files
    templates = [
        (".github/ISSUE_TEMPLATE/bug_report.md", bug_template),
        (".github/ISSUE_TEMPLATE/feature_request.md", feature_template),
        (".github/ISSUE_TEMPLATE/user_story.md", story_template)
    ]
    
    for file_path, content in templates:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Created template: {file_path}")

def main():
    print("🚀 Setting up GitHub Project Management for Transcripts MVP")
    print("=" * 60)
    
    # Setup all components
    setup_labels()
    setup_milestones()
    create_epic_issues()
    create_user_stories()
    create_project_board()
    setup_issue_templates()
    
    print("\n" + "=" * 60)
    print("✅ GitHub Project Management Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Visit https://github.com/GuillaumeRacine/Transcripts_MVP/issues")
    print("2. Review and adjust the created issues")
    print("3. Add issues to your project board")
    print("4. Start working on high-priority items")
    print("5. Use the issue templates for new bugs/features")
    
    print("\n🎯 Quick Commands:")
    print("- List issues: gh issue list")
    print("- View projects: gh project list")
    print("- Create new issue: gh issue create")
    print("- View milestones: gh api repos/GuillaumeRacine/Transcripts_MVP/milestones")

if __name__ == "__main__":
    main()