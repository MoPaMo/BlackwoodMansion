from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import time
import os
import random

@dataclass
class Evidence:
    name: str
    description: str
    tags: Set[str]  # Categories like "technical", "medical", "personal"

@dataclass
class GameState:
    inventory: List[str]
    evidence: List[Evidence]
    flags: Dict[str, bool]
    current_location: str
    relationships: Dict[str, int]  # Now placed before default fields
    time_remaining: int = 24  # Hours until storm
    stress_level: int = 0  # Affects some choices
    current_track: str = "none"  # Technical, personal, or medical

@dataclass
class Choice:
    description: str
    next_location: str
    required_items: List[str] = None
    required_flags: Dict[str, bool] = None
    required_evidence: List[str] = None
    time_cost: int = 1
    stress_change: int = 0
    inventory_add: List[str] = None
    inventory_remove: List[str] = None
    flags_change: Dict[str, bool] = None
    evidence_add: List[Evidence] = None
    relationship_changes: Dict[str, int] = None
    track_change: str = None

class Location:
    def __init__(self, name: str, description: str, choices: Dict[str, Choice],
                 time_descriptions: Dict[int, str] = None):
        self.name = name
        self.description = description
        self.choices = choices
        # Different descriptions based on time remaining
        self.time_descriptions = time_descriptions or {}

class BlackwoodMansionGame:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.state = GameState(
            inventory=[],
            evidence=[],
            flags={},
            current_location="mansion_entrance",
            relationships={
                "elena": 0,
                "james": 0,
                "victoria": 0,
                "gregory": 0,
                "ada": 0
            }
        )
        self.setup_game()
    
    def setup_game(self):
        self.create_locations()
        self.create_evidence_database()
    
    def create_evidence_database(self):
        # Define all possible evidence that can be collected
        self.all_evidence = {
            "server_logs": Evidence(
                "Server Logs",
                "Corrupted logs from Ada's main system",
                {"technical", "ai"}
            ),
            "medical_records": Evidence(
                "Medical Records",
                "Marcus's recent medical history",
                {"medical"}
            ),
        }
    
    def create_locations(self):
        # Mansion Entrance
        entrance = Location(
            "mansion_entrance",
            "You stand before Blackwood Manor. Rain pours down as thunder crashes overhead.",
            {
                "front_door": Choice(
                    "Enter through the front door",
                    "main_hall",
                    time_cost=1,
                    flags_change={"formal_entry": True}
                ),
                "examine_exterior": Choice(
                    "Examine the mansion exterior",
                    "mansion_exterior",
                    time_cost=1,
                    stress_change=1,
                    evidence_add=[Evidence(
                        "Broken Window",
                        "A partially opened window on the second floor",
                        {"personal", "security"}
                    )]
                ),
                "security_office": Choice(
                    "Head to the security office",
                    "security_office",
                    time_cost=1,
                    track_change="technical"
                )
            },
            {
                12: "The storm is getting worse. Time is running out.",
                6: "The wind howls violently. You're almost out of time."
            }
        )
        
        # Main Hall
        main_hall = Location(
            "main_hall",
            "The grand hall is dimly lit. Elena and James stand near the staircase.",
            {
                "talk_elena": Choice(
                    "Interview Elena Blackwood",
                    "elena_conversation",
                    time_cost=2,
                    relationship_changes={"elena": 1}
                ),
                "talk_james": Choice(
                    "Question James the butler",
                    "james_conversation",
                    time_cost=2,
                    relationship_changes={"james": 1}
                ),
                "examine_hall": Choice(
                    "Search the hall for clues",
                    "main_hall_search",
                    time_cost=1,
                    evidence_add=[Evidence(
                        "Muddy Footprints",
                        "Fresh tracks leading to the study",
                        {"personal", "security"}
                    )]
                )
            }
        )
        
        # Security Office
        security_office = Location(
            "security_office",
            "Banks of monitors line the walls. Gregory Wells stands at attention.",
            {
                "check_footage": Choice(
                    "Review security footage",
                    "security_footage",
                    time_cost=2,
                    track_change="technical",
                    evidence_add=[Evidence(
                        "Camera Footage",
                        "Corrupted files from last night",
                        {"technical", "security"}
                    )]
                ),
                "question_gregory": Choice(
                    "Interview Gregory Wells",
                    "gregory_conversation",
                    time_cost=1,
                    relationship_changes={"gregory": 1}
                ),
                "examine_system": Choice(
                    "Investigate the security system",
                    "security_system",
                    required_flags={"tech_savvy": True},
                    time_cost=2,
                    evidence_add=[Evidence(
                        "System Breach",
                        "Evidence of recent unauthorized access",
                        {"technical", "security"}
                    )]
                )
            }
        )
        
        
        for location in [entrance, main_hall, security_office]:
            self.add_location(location)
    
    def add_location(self, location: Location):
        self.locations[location.name] = location
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def slow_print(self, text: str, delay: float = 0.03):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def display_status(self):
        print("\n" + "="*50)
        print(f"Time Remaining: {self.state.time_remaining} hours")
        print(f"Current Track: {self.state.current_track.title()}")
        print(f"Stress Level: {'▮' * self.state.stress_level}{'▯' * (10-self.state.stress_level)}")
        
        if self.state.inventory:
            print(f"\nInventory: {', '.join(self.state.inventory)}")
        
        if self.state.evidence:
            print("\nEvidence Collected:")
            for evidence in self.state.evidence:
                print(f"- {evidence.name}: {evidence.description}")
        
        print("="*50 + "\n")
    
    def can_make_choice(self, choice: Choice) -> bool:
        if choice.required_items and not all(item in self.state.inventory for item in choice.required_items):
            return False
        if choice.required_flags and not all(self.state.flags.get(flag) == value 
                                           for flag, value in choice.required_flags.items()):
            return False
        if choice.required_evidence and not all(any(e.name == req for e in self.state.evidence) 
                                              for req in choice.required_evidence):
            return False
        return True
    
    def apply_choice_effects(self, choice: Choice):
        self.state.time_remaining -= choice.time_cost
        self.state.stress_level = max(0, min(10, self.state.stress_level + choice.stress_change))
        
        if choice.inventory_add:
            self.state.inventory.extend(choice.inventory_add)
        if choice.inventory_remove:
            for item in choice.inventory_remove:
                if item in self.state.inventory:
                    self.state.inventory.remove(item)
        if choice.flags_change:
            self.state.flags.update(choice.flags_change)
        if choice.evidence_add:
            self.state.evidence.extend(choice.evidence_add)
        if choice.relationship_changes:
            for character, change in choice.relationship_changes.items():
                self.state.relationships[character] += change
        if choice.track_change:
            self.state.current_track = choice.track_change
    
    def check_ending_conditions(self) -> Optional[str]:
        if self.state.time_remaining <= 0:
            return "timeout"
        
        # AI Conspiracy Ending
        if (any(e.name == "Server Logs" for e in self.state.evidence) and
            self.state.flags.get("found_secret_server") and
            self.state.relationships["ada"] > 3):
            return "ai_conspiracy"
        
        # Perfect Crime Ending
        if (any(e.name == "Financial Records" for e in self.state.evidence) and
            self.state.flags.get("found_secret_passage") and
            self.state.relationships["elena"] < -2):
            return "perfect_crime"
        
        
        return None
    
    def play_ending(self, ending: str):
        self.clear_screen()
        if ending == "timeout":
            self.slow_print("The storm has made the mansion inaccessible. The investigation remains unsolved...")
        elif ending == "ai_conspiracy":
            self.slow_print("You've discovered the truth: Marcus's consciousness lives on in Ada...")
        elif ending == "perfect_crime":
            self.slow_print("Elena's perfect crime is revealed, but Marcus is beyond saving...")
    
    def play(self):
        while True:
            self.clear_screen()
            current_location = self.locations[self.state.current_location]
            
            self.display_status()
            
            # Get time-appropriate description
            description = current_location.description
            for time_threshold, time_desc in sorted(current_location.time_descriptions.items()):
                if self.state.time_remaining <= time_threshold:
                    description = time_desc
                    break
            
            self.slow_print(description)
            print("\nWhat would you like to do?\n")
            
            valid_choices = {}
            choice_num = 1
            
            for choice_id, choice in current_location.choices.items():
                if self.can_make_choice(choice):
                    valid_choices[str(choice_num)] = (choice_id, choice)
                    print(f"{choice_num}. {choice.description}")
                    choice_num += 1
            
            if not valid_choices:
                print("\nNo valid choices available - Investigation deadlocked")
                break
            
            choice = input("\nEnter your choice (number): ").strip()
            
            if choice not in valid_choices:
                continue
            
            choice_id, chosen_choice = valid_choices[choice]
            self.apply_choice_effects(chosen_choice)
            self.state.current_location = chosen_choice.next_location
            
            ending = self.check_ending_conditions()
            if ending:
                self.play_ending(ending)
                break

if __name__ == "__main__":
    game = BlackwoodMansionGame()
    game.play()