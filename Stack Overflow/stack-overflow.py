# Requirements

# 1. Users post questions, answer questions, and comment on questions and answers
# 2. Users can vote on questions and answers
# 3. Questions should have tags associated with them
# 4. users can search for questions based on keywords, tags or user profiles.
# 5. The system should assign reputation score to users based on their activity and the quality of their contributions.
# 6. The syatem should handle concurrent acsess and ensure data consistency.

import threading
import uuid
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set
from datetime import datetime

class VoteType(Enum):
    UPVOTE = "UPVOTE"
    DOWNVOTE = "DOWNVOTE"

class EventType(Enum):
    UPVOTE_QUESTION = "UPVOTE_QUESTION"
    DOWNVOTE_QUESTION = "DOWNVOTE_QUESTION"
    UPVOTE_ANSWER = "UPVOTE_ANSWER"
    DOWNVOTE_ANSWER = "DOWNVOTE_ANSWER"
    ACCEPT_ANSWER = "ACCEPT_ANSWER"

class User:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.reputation = 0
        self._lock = threading.Lock()

    def update_reputation(self, change: int):
        with self._lock:
            self.reputation += change

    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name
    
    def get_reputation(self):
        with self._lock:
            return self.reputation
        
class Tag:
    def __init__(self, name: str):
        self.name = name

    def get_name(self):
        return self.name
    
class Event:
    def __init__(self, event_type: EventType, actor: User, target_post: 'Post'):
        self.type = event_type
        self.actor = actor
        self.target_post = target_post

    def get_type(self):
        return self.type

    def get_actor(self):
        return self.actor
    
    def get_target_post(self):
        return self.target_post

class PostObserver(ABC):
    @abstractmethod
    def on_post_event(self, event: Event):
        pass

class ReutationManager(PostObserver):
    QUESTION_UPVOTE_REP = 5
    ANSWER_UPVOTE_REP = 10
    ACCEPTED_ANSWER_REP = 15
    DOWNVOTE_REP_PENALTY = -1
    POST_DOWNVOTED_REP_PENALTY = -2

    def on_post_event(self, event: Event):
        post_author = event.get_target_post().get_author()

        if event.get_type() == EventType.UPVOTE_QUESTION:
            post_author.update_reputation(self.QUESTION_UPVOTE_REP)
        elif event.get_type() == EventType.DOWNVOTE_QUESTION:
            post_author.update_reputation(self.DOWNVOTE_REP_PENALTY)
            event.get_actor().update_reputation(self.POST_DOWNVOTED_REP_PENALTY)  # voter penalty
        elif event.get_type() == EventType.UPVOTE_ANSWER:
            post_author.update_reputation(self.ANSWER_UPVOTE_REP)
        elif event.get_type() == EventType.DOWNVOTE_ANSWER:
            post_author.update_reputation(self.DOWNVOTE_REP_PENALTY)
            event.get_actor().update_reputation(self.POST_DOWNVOTED_REP_PENALTY)
        elif event.get_type() == EventType.ACCEPT_ANSWER:
            post_author.update_reputation(self.ACCEPTED_ANSWER_REP)

class Content(ABC):
    def __init__(self, content_id: str, body: str, author: User):
        self.id = content_id
        self.body = body
        self.author = author
        self.creation_time = datetime.now()

    def get_id(self):
        return self.id
    
    def get_body(self):
        return self.body
    
    def get_author(self):
        return self.author
    
class Post(Content):
    def __init__(self, content_id: str, body: str, author: User):
        super().__init__(content_id, body, author)
        self.vote_count = 0
        self.voters: Dict[str, VoteType] = {}
        self.comments: List['Comment'] = []
        self.observers: List[PostObserver] = []
        self._lock = threading.Lock()

    def add_observer(self, observer: PostObserver):
        self.observers.append(observer)

    def notify_observers(self, event: Event):
        for oberser in self.observers:
            oberser.on_post_event(event)

    def vote(self, user: User, vote_type: VoteType):
        with self._lock:
            user_id = user.get_id()
            if self.voters.get(user_id) == vote_type:
                return
            
            score_change = 0
            if user_id in self.voters:
                score_change = 2 if vote_type == VoteType.UPVOTE else -2
            else:
                score_change = 1 if vote_type == VoteType.UPVOTE else -1

            self.voters[user_id] = vote_type
            self.vote_count += score_change

            if isinstance(self, Question):
                event_type = EventType.UPVOTE_QUESTION if vote_type == VoteType.UPVOTE else EventType.DOWNVOTE_QUESTION
            else:
                event_type = EventType.UPVOTE_ANSWER if vote_type == VoteType.UPVOTE else EventType.DOWNVOTE_ANSWER

            self.notify_observers(Event(event_type, user, self))

    def get_vote_count(self):
        return self.vote_count
    
    def add_comment(self, comment: 'Comment'):
        self.comments.append(comment)

    def get_comments(self):
        return self.comments
    
class Question(Post):
    def __init__(self, title: str, body: str, author: User, tags: Set[Tag]):
        super().__init__(str(uuid.uuid4()), body, author)
        self.title = title
        self.tags = tags
        self.answers: List['Answer'] = []
        self.accepted_answer: Optional['Answer'] = None

    def add_answer(self, answer: 'Answer'):
        self.answers.append(answer)

    def accept_answer(self, answer: 'Answer'):
        with self._lock:
            if (self.author.get_id() != answer.get_author().get_id() and 
                self.accepted_answer is None):
                self.accepted_answer = answer
                answer.set_accepted(True)
                self.notify_observers(Event(EventType.ACCEPT_ANSWER, answer.get_author(), answer))
        
    def get_title(self):
        return self.title
    
    def get_tags(self):
        return self.tags
    
    def get_answers(self):
        return self.answers
    
    def get_accepted_answer(self):
        return self.accepted_answer
    
class Answer(Post):
    def __init__(self, body: str, author: User):
        super().__init__(str(uuid.uuid4()), body, author)
        self.is_accepted = False

    def set_accepted(self, accepted: bool):
        self.is_accepted = accepted

    def is_accepted_answer(self) -> bool:
        return self.is_accepted

class Comment(Content):
    def __init__(self, body: str, author: User):
        super().__init__(str(uuid.uuid4()), body, author)

class SearchStrategy(ABC):
    @abstractmethod
    def filter(self, questions: List[Question]):
        pass

class keywordSearchStrategy(SearchStrategy):
    def __init__(self, keyword: str):
        self.keyword = keyword

    def filter(self, questions: List[Question]):
        return [q for q in questions
                if self.keyword in q.get_title().lower() or self.keyword in q.get_body().lower()]
    
class TagSearchStrategy(SearchStrategy):
    def __init__(self, tag: Tag):
        self.tag = tag

    def filter(self, questions: List[Question]):
        return [q for q in questions
                if any(t.get_name().lower() == self.tag.get_name().lower() for t in q.get_tags())]
    
class UserSearchStrategy(SearchStrategy):
    def __init__(self, user: User):
        self.user = user

    def filter(self, questions: List[Question]) -> List[Question]:
        return [q for q in questions if q.get_author().get_id() == self.user.get_id()]
    
class StackOverflowService:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.questions: Dict[str, Question] = {}
        self.answers: Dict[str, Answer] ={}
        self.reputation_manager = ReutationManager()

    def create_user(self, name: str):
        user = User(name)
        self.users[user.get_id()] = user
        return user
    
    def post_question(self, user_id: str, title: str, body: str, tags: Set[Tag]):
        author = self.users[user_id]
        question = Question(title, body, author, tags)
        self.questions[question.get_id()] = question
        return question
    
    def post_answer(self, user_id: str, question_id: str, body: str):
        author = self.users[user_id]
        question = self.questions[question_id]
        answer = Answer(body, author)
        answer.add_observer(self.reputation_manager)
        question.add_answer(answer)
        self.answers[answer.get_id()] = answer
        return answer
    
    def vote_on_post(self, user_id: str, post_id: str, vote_type: VoteType):
        user = self.users[user_id]
        post = self.find_post_by_id(post_id)
        post.vote(user, vote_type)

    def accept_answer(self, question_id: str, answer_id: str):
        question = self.questions[question_id]
        answer = self.answers[answer_id]
        question.accept_answer(answer)

    def search_questions(self, startegies: List[SearchStrategy]):
        results = list(self.questions.values())

        for strategy in startegies:
            results = strategy.filter(results)
        
        return results
    
    def get_user(self, user_id: str):
        return self.users[user_id]
    
    def find_post_by_id(self, post_id: str):
        if post_id in self.questions:
            return self.questions[post_id]
        elif post_id in self.answers:
            return self.answers[post_id]
        return KeyError("Post Not found")
    

class StackOverflowDemo:
    @staticmethod
    def main():
        service = StackOverflowService()

        # 1. Create Users
        alice = service.create_user("Alice")
        bob = service.create_user("Bob")
        charlie = service.create_user("Charlie")

        # 2. Alice posts a question
        print("--- Alice posts a question ---")
        java_tag = Tag("java")
        design_patterns_tag = Tag("design-patterns")
        tags = {java_tag, design_patterns_tag}
        question = service.post_question(alice.get_id(), "How to implement Observer Pattern?", "Details about Observer Pattern...", tags)
        StackOverflowDemo.print_reputations(alice, bob, charlie)

        # 3. Bob and Charlie post answers
        print("\n--- Bob and Charlie post answers ---")
        bob_answer = service.post_answer(bob.get_id(), question.get_id(), "You can use the java.util.Observer interface.")
        charlie_answer = service.post_answer(charlie.get_id(), question.get_id(), "A better way is to create your own Observer interface.")
        StackOverflowDemo.print_reputations(alice, bob, charlie)

        # 4. Voting happens
        print("\n--- Voting Occurs ---")
        service.vote_on_post(alice.get_id(), question.get_id(), VoteType.UPVOTE)  # Alice upvotes her own question
        service.vote_on_post(bob.get_id(), charlie_answer.get_id(), VoteType.UPVOTE)  # Bob upvotes Charlie's answer
        service.vote_on_post(alice.get_id(), bob_answer.get_id(), VoteType.DOWNVOTE)  # Alice downvotes Bob's answer
        StackOverflowDemo.print_reputations(alice, bob, charlie)

        # 5. Alice accepts Charlie's answer
        print("\n--- Alice accepts Charlie's answer ---")
        service.accept_answer(question.get_id(), charlie_answer.get_id())
        StackOverflowDemo.print_reputations(alice, bob, charlie)

        # 6. Search for questions
        print("\n--- (C) Combined Search: Questions by 'Alice' with tag 'java' ---")
        filters_c = [
            UserSearchStrategy(alice),
            TagSearchStrategy(java_tag)
        ]
        search_results = service.search_questions(filters_c)
        for q in search_results:
            print(f"  - Found: {q.get_title()}")

    @staticmethod
    def print_reputations(*users):
        print("--- Current Reputations ---")
        for user in users:
            print(f"{user.get_name()}: {user.get_reputation()}")


if __name__ == "__main__":
    StackOverflowDemo.main()