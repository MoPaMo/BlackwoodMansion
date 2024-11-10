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
        self.create_evidence_database()
        self.create_locations()

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
            "financial_records": Evidence(
                "Financial Records",
                "Suspicious financial transactions linked to Elena",
                {"financial", "personal"}
            ),
            "broken_window": Evidence(
                "Broken Window",
                "A partially opened window on the second floor",
                {"personal", "security"}
            ),
            "muddy_footprints": Evidence(
                "Muddy Footprints",
                "Fresh tracks leading to the study",
                {"personal", "security"}
            ),
            "camera_footage": Evidence(
                "Camera Footage",
                "Corrupted files from last night",
                {"technical", "security"}
            ),
            "system_breach": Evidence(
                "System Breach",
                "Evidence of recent unauthorized access",
                {"technical", "security"}
            ),
            "secret_passage_map": Evidence(
                "Secret Passage Map",
                "A map revealing hidden passages within the mansion",
                {"personal", "secret"}
            )
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
                    evidence_add=[self.all_evidence["broken_window"]]
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

        # Mansion Exterior (Added Tool Shed and Library access)
        mansion_exterior = Location(
            "mansion_exterior",
            "The grand exterior of the mansion is imposing. Amidst the storm, you notice a side shed and windows that might be accessible.",
            {
                "enter_library": Choice(
                    "Enter the library",
                    "library",
                    time_cost=1
                ),
                "enter_tool_shed": Choice(
                    "Enter the tool shed",
                    "tool_shed",
                    time_cost=1
                ),
                "return_entrance": Choice(
                    "Return to the entrance",
                    "mansion_entrance",
                    time_cost=1
                )
            },
            {
                12: "The storm intensifies, making it harder to stay outside.",
                6: "Lightning flashes illuminate the surrounding gardens."
            }
        )

        # Tool Shed
        tool_shed = Location(
            "tool_shed",
            "A small shed filled with various tools and equipment.",
            {
                "search_tools": Choice(
                    "Search the shed for useful tools",
                    "search_tools_result",
                    time_cost=1,
                    inventory_add=["lockpick"],
                    flags_change={"searched_toolshed": True},
                    required_flags={"searched_toolshed": False}
                ),
                "leave_shed": Choice(
                    "Leave the shed",
                    "mansion_exterior",
                    time_cost=1
                )
            }
        )

        # Search Tools Result
        search_tools_result = Location(
            "search_tools_result",
            "You find a sturdy lockpick lying among the tools. It might prove useful.",
            {
                "take_lockpick": Choice(
                    "Take the lockpick",
                    "tool_shed",
                    time_cost=0,
                    inventory_add=["lockpick"]
                ),
                "leave_lockpick": Choice(
                    "Leave the lockpick and continue",
                    "tool_shed",
                    time_cost=0
                )
            }
        )

        # Library
        library = Location(
            "library",
            "Rows of old books line the walls. Ada is meticulously organizing some volumes.",
            {
                "search_books": Choice(
                    "Search the books for hidden clues",
                    "search_books_result",
                    time_cost=2,
                    evidence_add=[self.all_evidence["secret_passage_map"]],
                    required_flags={"searched_library": False},
                    flags_change={"searched_library": True}
                ),
                "talk_ada": Choice(
                    "Talk to Ada about the family's history",
                    "ada_conversation",
                    time_cost=1,
                    relationship_changes={"ada": 1}
                ),
                "leave_library": Choice(
                    "Leave the library",
                    "main_hall",
                    time_cost=1
                )
            },
            {
                12: "The storm is getting worse. Time is running out.",
                6: "The wind howls violently. You're almost out of time."
            }
        )

        # Search Books Result
        search_books_result = Location(
            "search_books_result",
            "While searching through the dusty volumes, you find a hidden lever behind a bookshelf.",
            {
                "pull_lever": Choice(
                    "Pull the lever to reveal a secret passage",
                    "secret_passage",
                    time_cost=1,
                    flags_change={"revealed_secret_passage": True}
                ),
                "ignore_lever": Choice(
                    "Ignore the lever and continue searching",
                    "library",
                    time_cost=1
                )
            }
        )

        # Secret Passage
        secret_passage = Location(
            "secret_passage",
            "A narrow, dimly lit passageway. The air is musty, and it seems to lead deeper into the mansion.",
            {
                "proceed_deeper": Choice(
                    "Proceed deeper into the mansion",
                    "hidden_room",
                    time_cost=3,
                    flags_change={"found_secret_passage": True}
                ),
                "return_main_hall": Choice(
                    "Return to the Main Hall",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Hidden Room
        hidden_room = Location(
            "hidden_room",
            "A hidden chamber filled with old artifacts and a single glowing computer terminal.",
            {
                "investigate_terminal": Choice(
                    "Investigate the computer terminal",
                    "terminal_investigation",
                    time_cost=2,
                    evidence_add=[self.all_evidence["server_logs"]],
                    required_flags={"found_secret_passage": True}
                ),
                "search_room": Choice(
                    "Search the room thoroughly",
                    "search_room_result",
                    time_cost=2,
                    evidence_add=[self.all_evidence["system_breach"]],
                    required_flags={"found_secret_passage": True}
                ),
                "exit_hidden_room": Choice(
                    "Exit the hidden room",
                    "secret_passage",
                    time_cost=1
                )
            }
        )

        # Terminal Investigation
        terminal_investigation = Location(
            "terminal_investigation",
            "You access the computer terminal and uncover encrypted server logs.",
            {
                "decrypt_logs": Choice(
                    "Attempt to decrypt the server logs",
                    "decrypt_logs_result",
                    time_cost=3,
                    flags_change={"decrypted_logs": True}
                ),
                "exit_terminal": Choice(
                    "Exit the terminal",
                    "hidden_room",
                    time_cost=1
                )
            }
        )

        # Decrypt Logs Result
        decrypt_logs_result = Location(
            "decrypt_logs_result",
            "After several attempts, you successfully decrypt the logs, revealing suspicious AI activities.",
            {
                "analyze_logs": Choice(
                    "Analyze the decrypted logs",
                    "analyze_logs_result",
                    time_cost=2,
                    flags_change={"analyzed_logs": True}
                ),
                "leave_logs": Choice(
                    "Leave the logs and continue",
                    "terminal_investigation",
                    time_cost=1
                )
            }
        )

        # Analyze Logs Result
        analyze_logs_result = Location(
            "analyze_logs_result",
            "The logs indicate that Ada has been developing unauthorized AI protocols.",
            {
                "share_findings": Choice(
                    "Share your findings with Ada",
                    "ada_conversation",
                    time_cost=1,
                    relationship_changes={"ada": -1}
                ),
                "keep_findings": Choice(
                    "Keep the findings to yourself",
                    "hidden_room",
                    time_cost=1
                )
            }
        )

        # Search Room Result
        search_room_result = Location(
            "search_room_result",
            "You thoroughly search the room and find evidence of a recent system breach.",
            {
                "analyze_breach": Choice(
                    "Analyze the system breach evidence",
                    "analyze_breach_result",
                    time_cost=2,
                    evidence_add=[self.all_evidence["system_breach"]],
                    flags_change={"analyzed_breach": True}
                ),
                "leave_room": Choice(
                    "Leave the room",
                    "hidden_room",
                    time_cost=1
                )
            }
        )

        # Analyze Breach Result
        analyze_breach_result = Location(
            "analyze_breach_result",
            "The breach seems to be linked to external unauthorized access attempts.",
            {
                "report_breach": Choice(
                    "Report the breach to security",
                    "security_report",
                    time_cost=1,
                    relationship_changes={"gregory": 1}
                ),
                "ignore_breach": Choice(
                    "Ignore the breach and continue",
                    "hidden_room",
                    time_cost=1
                )
            }
        )

        # Security Report
        security_report = Location(
            "security_report",
            "You inform Gregory about the breach, and he commends your vigilance.",
            {
                "continue_investigation": Choice(
                    "Continue your investigation",
                    "hidden_room",
                    time_cost=1
                ),
                "take_break": Choice(
                    "Take a break before continuing",
                    "main_hall",
                    time_cost=1
                )
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
                    relationship_changes={"elena": -1 if self.state.relationships["elena"] > 3 else 1},
                    # Adjusted relationship change based on existing relationship
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
                    evidence_add=[self.all_evidence["muddy_footprints"]]
                ),
                "access_secret_passage": Choice(
                    "Use the secret passage",
                    "secret_passage",
                    time_cost=1,
                    required_flags={"found_secret_passage": True}
                )
            }
        )

        # Main Hall Search Result
        main_hall_search = Location(
            "main_hall_search",
            "You find muddy footprints leading towards the study.",
            {
                "follow_footprints": Choice(
                    "Follow the muddy footprints to the study",
                    "study",
                    time_cost=1
                ),
                "ignore_footprints": Choice(
                    "Ignore the footprints and continue searching",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Study
        study = Location(
            "study",
            "A quiet study room with a large mahogany desk. Gregory is reviewing some documents.",
            {
                "inspect_desk": Choice(
                    "Inspect the desk drawers",
                    "desk_inspect",
                    time_cost=1,
                    evidence_add=[self.all_evidence["financial_records"]],
                    required_items=["lockpick"],
                    required_flags={"inspected_desk": False},
                    flags_change={"inspected_desk": True}
                ),
                "talk_gregory": Choice(
                    "Talk to Gregory about recent events",
                    "gregory_conversation",
                    time_cost=1,
                    relationship_changes={"gregory": 1}
                ),
                "leave_study": Choice(
                    "Leave the study",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Desk Inspect Result
        desk_inspect = Location(
            "desk_inspect",
            "Using your lockpick, you successfully open the desk drawer and find Elena's financial records.",
            {
                "analyze_records": Choice(
                    "Analyze the financial records",
                    "analyze_records_result",
                    time_cost=2,
                    evidence_add=[self.all_evidence["financial_records"]],
                    flags_change={"analyzed_financial_records": True}
                ),
                "leave_drawer": Choice(
                    "Leave the drawer and continue",
                    "study",
                    time_cost=1
                )
            }
        )

        # Analyze Records Result
        analyze_records_result = Location(
            "analyze_records_result",
            "The financial records reveal significant embezzlement by Elena to cover the family's debts.",
            {
                "confront_elena": Choice(
                    "Confront Elena with the evidence",
                    "elena_confrontation",
                    time_cost=1,
                    relationship_changes={"elena": -3}
                ),
                "hide_evidence": Choice(
                    "Hide the evidence and continue",
                    "study",
                    time_cost=1
                )
            }
        )

        # Elena Confrontation
        elena_confrontation = Location(
            "elena_confrontation",
            "Elena's demeanor changes as she becomes defensive and angry upon seeing the evidence.",
            {
                "press_further": Choice(
                    "Press Elena for more details",
                    "elena_reveal",
                    time_cost=2,
                    relationship_changes={"elena": -1},
                    flags_change={"elena_revealed": True}
                ),
                "end_confrontation": Choice(
                    "End the confrontation",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Conversations
        elena_conversation = Location(
            "elena_conversation",
            "Elena sits down with you, her expression guarded.",
            {
                "elena_reveal": Choice(
                    "Press Elena for more information",
                    "elena_reveal",
                    time_cost=2,
                    relationship_changes={"elena": -1},
                    flags_change={"elena_revealed": True}
                ),
                "get_back": Choice(
                    "Steer the conversation elsewhere",
                    "main_hall",
                    time_cost=1
                )
            }
        )


        james_conversation = Location(
            "james_conversation",
            "James looks nervous as you begin questioning him.",
            {
                "james_reveal": Choice(
                    "Question James about his activities last night",
                    "james_reveal",
                    time_cost=2,
                    relationship_changes={"james": 1},
                    flags_change={"james_revealed": True}
                ),
                "end_conversation": Choice(
                    "End the conversation",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        ada_conversation = Location(
            "ada_conversation",
            "Ada greets you warmly, her eyes flickering with artificial intelligence.",
            {
                "ask_about_ai": Choice(
                    "Ask Ada about her AI systems",
                    "ada_ai_info",
                    time_cost=2,
                    relationship_changes={"ada": 1},
                    flags_change={"ada_ai_info": True}
                ),
                "discuss_family": Choice(
                    "Discuss the Blackwood family history",
                    "ada_family_history",
                    time_cost=2,
                    relationship_changes={"ada": 1}
                )
            }
        )

        # Adding Conversation Outcome Locations with Empty Choices
        # These will be handled directly and won't display options to the player
        # To prevent dead ends, ensure that after the outcome, the player is returned to a valid location
        dummy_conversation_outcome = Location(
            "conversation_outcome",
            "",  # Description will be handled in handle_conversation_outcome
            {}
        )

        # Add all new locations to the game
        all_new_locations = [
            entrance, mansion_exterior, tool_shed, search_tools_result, library, search_books_result,
            secret_passage, hidden_room, terminal_investigation, decrypt_logs_result,
            analyze_logs_result, search_room_result, analyze_breach_result, security_report,
            main_hall, main_hall_search, study, desk_inspect, analyze_records_result,
            elena_confrontation, elena_conversation, james_conversation, ada_conversation
        ]
        for location in all_new_locations:
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

    def play_conversation(self, conversation_location: str):
        # Handle conversations without transitioning to separate Locations
        self.clear_screen()
        current_location = self.locations[conversation_location]
        self.display_status()
        self.slow_print(current_location.description)
        print("\nWhat would you like to do?\n")

        valid_choices = {}
        choice_num = 1

        for choice_id, choice in current_location.choices.items():
            if self.can_make_choice(choice):
                valid_choices[str(choice_num)] = (choice_id, choice)
                print(f"{choice_num}. {choice.description}")
                choice_num += 1

        if not valid_choices:
            print("\nNo valid choices available in this conversation.")
            return

        choice = input("\nEnter your choice (number): ").strip()

        if choice not in valid_choices:
            return

        choice_id, chosen_choice = valid_choices[choice]
        self.apply_choice_effects(chosen_choice)
        outcome = chosen_choice.next_location

        # Handle specific conversation outcomes
        if outcome in ["elena_reveal", "james_reveal", "ada_ai_info", "ada_family_history"]:
            self.handle_conversation_outcome(outcome)

        # After handling, return to main_hall
        self.state.current_location = "main_hall"

    def handle_conversation_outcome(self, outcome: str):
        self.clear_screen()
        if outcome == "elena_reveal":
            self.slow_print("Elena hesitates before admitting that she has been embezzling funds to cover the family's debts.")
        elif outcome == "james_reveal":
            self.slow_print("James nervously confesses that he was in the library studying after hours.")
        elif outcome == "ada_ai_info":
            self.slow_print("Ada explains that her AI systems have been upgraded recently, allowing her deeper integration with the mansion's systems.")
        elif outcome == "ada_family_history":
            self.slow_print("Ada shares that the Blackwood family has a long history of wealth and secrets that have been protected through generations.")
        input("\nPress Enter to return to the main hall...")

    def check_ending_conditions(self) -> Optional[str]:
        if self.state.time_remaining <= 0:
            return "timeout"

        # AI Conspiracy Ending
        if (any(e.name == "Server Logs" for e in self.state.evidence) and
            self.state.flags.get("found_secret_passage", False) and
            self.state.relationships["ada"] > 3):
            return "ai_conspiracy"

        # Perfect Crime Ending
        if (any(e.name == "Financial Records" for e in self.state.evidence) and
            self.state.flags.get("found_secret_passage", False) and
            self.state.relationships["elena"] < -2):
            return "perfect_crime"

        # System Breach Ending
        if (any(e.name == "System Breach" for e in self.state.evidence) and
            self.state.relationships["gregory"] > 2):
            return "system_breach_ending"

        # Personal Tragedy Ending
        if (self.state.stress_level >= 10):
            return "personal_tragedy"

        return None

    def play_ending(self, ending: str):
        self.clear_screen()
        if ending == "timeout":
            self.slow_print("The storm has made the mansion inaccessible. The investigation remains unsolved...")
        elif ending == "ai_conspiracy":
            self.slow_print("You've discovered the truth: Marcus's consciousness lives on in Ada, revealing a complex AI conspiracy.")
        elif ending == "perfect_crime":
            self.slow_print("Elena's perfect crime is unveiled, but Marcus's essence remains trapped within Ada's system.")
        elif ending == "system_breach_ending":
            self.slow_print("The system breach leads you to uncover dark secrets about Gregory's involvement in the family's downfall.")
        elif ending == "personal_tragedy":
            self.slow_print("The mounting stress overwhelmed you, and the mysteries of Blackwood Manor remain unsolved.")
        input("\nPress Enter to exit the game...")

    def play(self):
        while True:
            self.clear_screen()
            current_location = self.locations[self.state.current_location]

            self.display_status()

            # Get time-appropriate description
            description = current_location.description
            for time_threshold, time_desc in sorted(current_location.time_descriptions.items(), reverse=True):
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

            # Check if entered a conversation location
            if self.state.current_location in ["elena_conversation", "james_conversation", "ada_conversation"]:
                self.play_conversation(self.state.current_location)
                continue  # Continue the main loop

            ending = self.check_ending_conditions()
            if ending:
                self.play_ending(ending)
                break

if __name__ == "__main__":
    game = BlackwoodMansionGame()
    game.play()
