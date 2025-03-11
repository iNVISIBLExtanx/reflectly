from datetime import datetime
from bson import ObjectId

class GoalTracker:
    """
    Class for tracking and analyzing user goals.
    """
    
    def __init__(self, db):
        """
        Initialize the goal tracker.
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
    
    def create_goal(self, user_email, goal_data):
        """
        Create a new goal for a user.
        
        Args:
            user_email (str): The user's email
            goal_data (dict): Goal data including title, description, and target date
            
        Returns:
            str: ID of the created goal
        """
        goal = {
            'user_email': user_email,
            'title': goal_data['title'],
            'description': goal_data.get('description', ''),
            'target_date': goal_data.get('target_date'),
            'progress': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'milestones': goal_data.get('milestones', []),
            'completed': False
        }
        
        result = self.db.goals.insert_one(goal)
        return str(result.inserted_id)
    
    def update_progress(self, goal_id, progress):
        """
        Update the progress of a goal.
        
        Args:
            goal_id (str): ID of the goal
            progress (int): New progress value (0-100)
            
        Returns:
            bool: True if the goal was completed with this update, False otherwise
        """
        # Ensure progress is between 0 and 100
        progress = max(0, min(100, progress))
        
        # Check if goal was already completed
        goal = self.db.goals.find_one({'_id': ObjectId(goal_id)})
        was_completed = goal.get('completed', False)
        
        # Update goal progress
        self.db.goals.update_one(
            {'_id': ObjectId(goal_id)},
            {
                '$set': {
                    'progress': progress,
                    'updated_at': datetime.now(),
                    'completed': progress >= 100
                }
            }
        )
        
        # Return True if the goal was just completed
        return progress >= 100 and not was_completed
    
    def get_user_goals(self, user_email, include_completed=True):
        """
        Get all goals for a user.
        
        Args:
            user_email (str): The user's email
            include_completed (bool): Whether to include completed goals
            
        Returns:
            list: List of goals
        """
        query = {'user_email': user_email}
        
        if not include_completed:
            query['completed'] = False
        
        goals = list(self.db.goals.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for goal in goals:
            goal['_id'] = str(goal['_id'])
        
        return goals
    
    def get_goal_by_id(self, goal_id):
        """
        Get a goal by its ID.
        
        Args:
            goal_id (str): ID of the goal
            
        Returns:
            dict: Goal data or None if not found
        """
        goal = self.db.goals.find_one({'_id': ObjectId(goal_id)})
        
        if goal:
            goal['_id'] = str(goal['_id'])
        
        return goal
    
    def add_milestone(self, goal_id, milestone_data):
        """
        Add a milestone to a goal.
        
        Args:
            goal_id (str): ID of the goal
            milestone_data (dict): Milestone data including title and target date
            
        Returns:
            str: ID of the created milestone
        """
        milestone = {
            '_id': ObjectId(),
            'title': milestone_data['title'],
            'target_date': milestone_data.get('target_date'),
            'completed': False,
            'created_at': datetime.now()
        }
        
        self.db.goals.update_one(
            {'_id': ObjectId(goal_id)},
            {
                '$push': {'milestones': milestone},
                '$set': {'updated_at': datetime.now()}
            }
        )
        
        return str(milestone['_id'])
    
    def complete_milestone(self, goal_id, milestone_id):
        """
        Mark a milestone as completed.
        
        Args:
            goal_id (str): ID of the goal
            milestone_id (str): ID of the milestone
            
        Returns:
            bool: True if successful, False otherwise
        """
        result = self.db.goals.update_one(
            {
                '_id': ObjectId(goal_id),
                'milestones._id': ObjectId(milestone_id)
            },
            {
                '$set': {
                    'milestones.$.completed': True,
                    'milestones.$.completed_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        
        return result.modified_count > 0
    
    def analyze_goal_progress(self, user_email):
        """
        Analyze the progress of all goals for a user.
        
        Args:
            user_email (str): The user's email
            
        Returns:
            dict: Analysis results
        """
        goals = self.get_user_goals(user_email)
        
        # Calculate statistics
        total_goals = len(goals)
        completed_goals = sum(1 for goal in goals if goal.get('completed', False))
        active_goals = total_goals - completed_goals
        
        # Calculate average progress for active goals
        if active_goals > 0:
            active_goal_progress = [goal['progress'] for goal in goals if not goal.get('completed', False)]
            avg_progress = sum(active_goal_progress) / len(active_goal_progress)
        else:
            avg_progress = 0
        
        # Get goals due soon (within 7 days)
        now = datetime.now()
        due_soon = []
        for goal in goals:
            if goal.get('target_date') and not goal.get('completed', False):
                target_date = goal['target_date']
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                
                days_remaining = (target_date - now).days
                if 0 <= days_remaining <= 7:
                    due_soon.append({
                        'id': goal['_id'],
                        'title': goal['title'],
                        'days_remaining': days_remaining,
                        'progress': goal['progress']
                    })
        
        return {
            'total_goals': total_goals,
            'completed_goals': completed_goals,
            'active_goals': active_goals,
            'completion_rate': completed_goals / total_goals if total_goals > 0 else 0,
            'average_progress': avg_progress,
            'goals_due_soon': due_soon
        }
