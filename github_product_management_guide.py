#!/usr/bin/env python3
"""
GitHub Product Management Automation Scripts
Demonstrates how to use GitHub CLI for product development workflows
"""

import subprocess
import json
from datetime import datetime, timedelta

class GitHubProductManager:
    """Automate GitHub operations for product management"""
    
    def __init__(self, repo_owner, repo_name):
        self.owner = repo_owner
        self.repo = repo_name
        self.repo_full = f"{repo_owner}/{repo_name}"
    
    def create_product_milestone(self, title, description, due_date=None):
        """Create a milestone for product releases"""
        cmd = [
            "gh", "api", f"repos/{self.repo_full}/milestones",
            "--method", "POST",
            "--field", f"title={title}",
            "--field", f"description={description}"
        ]
        
        if due_date:
            cmd.extend(["--field", f"due_on={due_date.isoformat()}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            milestone = json.loads(result.stdout)
            print(f"✅ Created milestone: {title} (#{milestone['number']})")
            return milestone
        else:
            print(f"❌ Failed to create milestone: {result.stderr}")
            return None
    
    def create_feature_epic(self, title, description, labels=None, milestone=None):
        """Create a high-level epic issue for major features"""
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", description
        ]
        
        if labels:
            for label in labels:
                cmd.extend(["--label", label])
        
        if milestone:
            cmd.extend(["--milestone", milestone])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created epic: {title}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create epic: {result.stderr}")
            return None
    
    def create_user_story(self, title, story, acceptance_criteria, labels=None, epic_number=None):
        """Create user story issues with proper formatting"""
        
        body = f"""## User Story
{story}

## Acceptance Criteria
{acceptance_criteria}

## Definition of Done
- [ ] Code implemented and tested
- [ ] UI/UX reviewed and approved
- [ ] Documentation updated
- [ ] Stakeholder sign-off received
"""
        
        if epic_number:
            body += f"\n## Related Epic\nCloses #{epic_number}\n"
        
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", body
        ]
        
        if labels:
            for label in labels:
                cmd.extend(["--label", label])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created user story: {title}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create user story: {result.stderr}")
            return None
    
    def create_bug_report(self, title, description, steps_to_reproduce, expected_behavior, actual_behavior):
        """Create properly formatted bug reports"""
        
        body = f"""## Bug Description
{description}

## Steps to Reproduce
{steps_to_reproduce}

## Expected Behavior
{expected_behavior}

## Actual Behavior
{actual_behavior}

## Environment
- Browser: [e.g., Chrome 91]
- OS: [e.g., macOS 12.0]
- Device: [e.g., MacBook Pro]

## Additional Context
[Add any other context about the problem here]
"""
        
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body", body,
            "--label", "bug",
            "--label", "needs-triage"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created bug report: {title}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create bug report: {result.stderr}")
            return None
    
    def setup_project_board(self, project_name, description):
        """Create a project board for tracking work"""
        cmd = [
            "gh", "project", "create",
            "--title", project_name,
            "--body", description
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created project board: {project_name}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create project board: {result.stderr}")
            return None
    
    def create_release(self, version, title, notes, is_prerelease=False):
        """Create a product release"""
        cmd = [
            "gh", "release", "create", version,
            "--title", title,
            "--notes", notes
        ]
        
        if is_prerelease:
            cmd.append("--prerelease")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created release: {version}")
            return result.stdout.strip()
        else:
            print(f"❌ Failed to create release: {result.stderr}")
            return None
    
    def bulk_create_labels(self, labels):
        """Create standard labels for product management"""
        for label_name, color, description in labels:
            cmd = [
                "gh", "api", f"repos/{self.repo_full}/labels",
                "--method", "POST",
                "--field", f"name={label_name}",
                "--field", f"color={color}",
                "--field", f"description={description}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Created label: {label_name}")
            else:
                print(f"⚠️ Label might already exist: {label_name}")

# Example usage and templates
def setup_product_development_workflow():
    """Example: Setting up a complete product development workflow"""
    
    # Initialize for your repo
    pm = GitHubProductManager("your-username", "your-repo")
    
    print("🚀 Setting up Product Development Workflow\n")
    
    # 1. Create standard labels
    print("📋 Creating standard labels...")
    labels = [
        ("epic", "purple", "Large feature or capability"),
        ("user-story", "blue", "User-facing functionality"),
        ("bug", "red", "Something isn't working"),
        ("enhancement", "green", "New feature or request"),
        ("priority:high", "orange", "High priority item"),
        ("priority:medium", "yellow", "Medium priority item"),
        ("priority:low", "lightgray", "Low priority item"),
        ("status:blocked", "black", "Work is blocked"),
        ("status:in-progress", "lightblue", "Currently being worked on"),
        ("status:review", "pink", "Needs review"),
        ("frontend", "lightgreen", "Frontend development"),
        ("backend", "brown", "Backend development"),
        ("design", "violet", "Design and UX work"),
        ("documentation", "gray", "Documentation updates")
    ]
    pm.bulk_create_labels(labels)
    
    # 2. Create milestones
    print("\n🎯 Creating product milestones...")
    mvp_date = datetime.now() + timedelta(days=30)
    v1_date = datetime.now() + timedelta(days=60)
    
    pm.create_product_milestone(
        "MVP Release", 
        "Minimum viable product with core features",
        mvp_date
    )
    
    pm.create_product_milestone(
        "v1.0 Release",
        "First stable release with full feature set",
        v1_date
    )
    
    # 3. Create epics
    print("\n📚 Creating feature epics...")
    auth_epic = pm.create_feature_epic(
        "Epic: User Authentication System",
        """## Overview
Implement complete user authentication and authorization system.

## Goals
- Secure user registration and login
- OAuth integration (Google, GitHub)
- Role-based access control
- Password reset functionality

## Success Metrics
- 95% successful login rate
- <2 second authentication response time
- Zero security vulnerabilities
""",
        labels=["epic", "priority:high", "backend"],
        milestone="MVP Release"
    )
    
    # 4. Create user stories
    print("\n👤 Creating user stories...")
    pm.create_user_story(
        "User can register with email and password",
        "As a new user, I want to create an account with my email and password so that I can access the platform.",
        """- User can enter email and password on registration form
- System validates email format and password strength
- User receives confirmation email
- Account is created and user is logged in
- Appropriate error messages for invalid inputs""",
        labels=["user-story", "frontend", "backend"],
        epic_number=1  # Assuming auth epic was #1
    )
    
    # 5. Create project board
    print("\n📊 Creating project board...")
    pm.setup_project_board(
        "Product Roadmap Q1 2024",
        "Track progress on major features and releases for Q1 2024"
    )
    
    print("\n✅ Product development workflow setup complete!")
    print("\n📋 Next steps:")
    print("1. Visit your GitHub repo to see created issues and milestones")
    print("2. Add issues to your project board")
    print("3. Start assigning team members to issues")
    print("4. Set up branch protection rules")
    print("5. Configure CI/CD workflows")

# Templates for common product management tasks
FEATURE_REQUEST_TEMPLATE = """
## Feature Request: [Feature Name]

### Problem Statement
[Describe the problem this feature solves]

### Proposed Solution
[Describe your proposed solution]

### User Personas Affected
- [ ] Power Users
- [ ] Casual Users  
- [ ] Administrators
- [ ] Developers

### Acceptance Criteria
- [ ] [Specific requirement 1]
- [ ] [Specific requirement 2]
- [ ] [Specific requirement 3]

### Success Metrics
- [How will we measure success?]

### Priority
- [ ] Must Have (P0)
- [ ] Should Have (P1)
- [ ] Could Have (P2)
- [ ] Won't Have This Time (P3)
"""

BUG_REPORT_TEMPLATE = """
## Bug Report: [Brief Description]

### Environment
- **Browser/App Version**: 
- **Operating System**: 
- **Device**: 

### Steps to Reproduce
1. [First step]
2. [Second step]
3. [Third step]

### Expected Behavior
[What should happen?]

### Actual Behavior
[What actually happens?]

### Screenshots/Videos
[If applicable, add screenshots or screen recordings]

### Additional Context
[Any other relevant information]

### Impact
- [ ] Critical (Blocks core functionality)
- [ ] High (Major feature unusable)
- [ ] Medium (Minor feature issue)
- [ ] Low (Cosmetic issue)
"""

if __name__ == "__main__":
    print("GitHub Product Management Guide")
    print("===============================")
    print("This script demonstrates GitHub CLI capabilities for product management.")
    print("Uncomment the line below to run the setup:")
    print("# setup_product_development_workflow()")