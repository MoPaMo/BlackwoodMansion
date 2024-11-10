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
                "ada": 0,
                "victoria": 0  # Added Victoria if not already present
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
        # Organize location creation into modular methods
        self.create_general_locations()
        self.create_security_office()
        self.create_victoria_conversation()
        self.create_marcus_investigation()

    def create_general_locations(self):
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
                ),
                "meet_victoria": Choice(
                    "Speak with Victoria in the eastern sitting room",
                    "victoria_conversation",
                    time_cost=1,
                    relationship_changes={"victoria": 1}
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
                "press_elena": Choice(
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

        # Add all general locations to the game
        all_general_locations = [
            entrance, mansion_exterior, tool_shed, search_tools_result, library, search_books_result,
            secret_passage, hidden_room, terminal_investigation, decrypt_logs_result,
            analyze_logs_result, search_room_result, analyze_breach_result, security_report,
            main_hall, main_hall_search, study, desk_inspect, analyze_records_result,
            elena_confrontation, elena_conversation, james_conversation, ada_conversation
        ]
        for location in all_general_locations:
            self.add_location(location)

    def create_security_office(self):
        # Security Office
        security_office = Location(
            "security_office",
            "You enter the security office, a room filled with surveillance monitors and security protocols. Gregory is here, overseeing the mansion's security systems.",
            {
                "check_surveillance": Choice(
                    "Check the latest surveillance footage",
                    "review_surveillance",
                    time_cost=2,
                    evidence_add=[self.all_evidence["camera_footage"]],
                    required_flags={"security_office_searched": False},
                    flags_change={"security_office_searched": True}
                ),
                "talk_gregory_sec": Choice(
                    "Talk to Gregory about the security breach",
                    "gregory_security_conversation",
                    time_cost=1,
                    relationship_changes={"gregory": 1}
                ),
                "leave_security_office": Choice(
                    "Leave the security office and return to the entrance",
                    "mansion_entrance",
                    time_cost=1
                )
            },
            {
                12: "The storm continues to rage outside, making the security systems even more crucial.",
                6: "The power fluctuations from the storm are affecting the security monitors."
            }
        )

        # Review Surveillance Result
        review_surveillance = Location(
            "review_surveillance",
            "You review the surveillance footage and notice suspicious activity near the library late last night.",
            {
                "investigate_suspicious_activity": Choice(
                    "Investigate the suspicious activity",
                    "library",
                    time_cost=1
                ),
                "secure_footage": Choice(
                    "Secure the surveillance footage for later analysis",
                    "security_office",
                    time_cost=1
                )
            }
        )

        # Gregory's Security Conversation
        gregory_security_conversation = Location(
            "gregory_security_conversation",
            "Gregory appears uneasy as you question him about the recent security breaches.",
            {
                "probe_further_sec": Choice(
                    "Probe further into the security breaches",
                    "gregory_reveal",
                    time_cost=2,
                    relationship_changes={"gregory": -1},
                    flags_change={"gregory_revealed": True}
                ),
                "change_topic_sec": Choice(
                    "Change the topic of conversation",
                    "security_office",
                    time_cost=1
                )
            }
        )

        # Add security-related locations to the game
        security_locations = [
            security_office,
            review_surveillance,
            gregory_security_conversation
        ]
        for location in security_locations:
            self.add_location(location)

    def create_victoria_conversation(self):
        # Victoria Conversation
        victoria_conversation = Location(
            "victoria_conversation",
            "Victoria looks serene as she sips her tea, but there's a hint of sadness in her eyes.",
            {
                "ask_about_marcus": Choice(
                    "Ask Victoria about Marcus's recent behavior",
                    "victoria_marcus_info",
                    time_cost=2,
                    relationship_changes={"victoria": 1},
                    flags_change={"victoria_marcus_info": True}
                ),
                "discuss_mansion_history": Choice(
                    "Discuss the history of Blackwood Manor",
                    "mansion_history",
                    time_cost=2
                ),
                "leave_victoria": Choice(
                    "Leave the conversation with Victoria",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Victoria's Marcus Information
        victoria_marcus_info = Location(
            "victoria_marcus_info",
            "Victoria mentions that Marcus has been acting strangely since the last storm.",
            {
                "investigate_behavior": Choice(
                    "Investigate Marcus's strange behavior",
                    "hidden_room",
                    time_cost=1
                ),
                "thank_victoria": Choice(
                    "Thank Victoria and return to the main hall",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Mansion History
        mansion_history = Location(
            "mansion_history",
            "Victoria shares tales of the Blackwood family's rise to prominence and the secrets they've kept hidden for generations.",
            {
                "ask_about_secrets": Choice(
                    "Ask Victoria about the family's secrets",
                    "victoria_secrets_info",
                    time_cost=2,
                    relationship_changes={"victoria": 1},
                    flags_change={"victoria_secrets_info": True}
                ),
                "end_history_discussion": Choice(
                    "End the discussion about history",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Victoria's Secrets Information
        victoria_secrets_info = Location(
            "victoria_secrets_info",
            "She whispers that there are hidden compartments throughout the mansion that hold untold stories and maybe some hidden treasures.",
            {
                "explore_hidden_compartments": Choice(
                    "Explore the hidden compartments",
                    "hidden_compartments",
                    time_cost=1
                ),
                "keep_information": Choice(
                    "Keep the information to yourself",
                    "mansion_history",
                    time_cost=1
                )
            }
        )

        # Hidden Compartments
        hidden_compartments = Location(
            "hidden_compartments",
            "Following Victoria's hints, you discover several hidden compartments behind bookcases and under carpets.",
            {
                "search_compartments": Choice(
                    "Search the hidden compartments for clues",
                    "compartments_search",
                    time_cost=2,
                    evidence_add=[self.all_evidence["secret_passage_map"]],
                    required_flags={"compartments_searched": False},
                    flags_change={"compartments_searched": True}
                ),
                "stop_searching": Choice(
                    "Stop searching and return to the main hall",
                    "mansion_history",
                    time_cost=1
                )
            }
        )

        # Compartments Search Result
        compartments_search = Location(
            "compartments_search",
            "In one of the compartments, you find a hidden map detailing secret passages within the mansion.",
            {
                "use_map": Choice(
                    "Use the secret passage map to find a way deeper into the mansion",
                    "secret_passage",
                    time_cost=1
                ),
                "store_map": Choice(
                    "Store the map for later use",
                    "main_hall",
                    time_cost=1,
                    inventory_add=["secret_passage_map"]
                )
            }
        )

        # Add Victoria-related locations to the game
        victoria_locations = [
            victoria_conversation, victoria_marcus_info, mansion_history,
            victoria_secrets_info, hidden_compartments, compartments_search
        ]
        for location in victoria_locations:
            self.add_location(location)

    def create_marcus_investigation(self):
        # Investigating Medical Records
        investigate_medical_records = Location(
            "investigate_medical_records",
            "Studying Marcus's medical records reveals that his condition has been deteriorating rapidly, possibly due to stress or unknown factors.",
            {
                "connect_to_ai": Choice(
                    "Connect Marcus's condition to Ada's AI systems",
                    "connect_ai_marcus",
                    time_cost=2,
                    relationship_changes={"ada": -1},
                    flags_change={"marcus_ai_connection": True}
                ),
                "report_health_issue": Choice(
                    "Report Marcus's health issues to a doctor",
                    "report_health",
                    time_cost=1
                )
            }
        )

        # Connecting Marcus's Condition to AI
        connect_ai_marcus = Location(
            "connect_ai_marcus",
            "You draw parallels between Marcus's declining health and Ada's recent system upgrades, suspecting a connection.",
            {
                "further_investigation_ai": Choice(
                    "Conduct a further investigation into the AI systems",
                    "terminal_investigation",
                    time_cost=1
                ),
                "hold_off_ai": Choice(
                    "Decide to hold off on the investigation",
                    "investigate_medical_records",
                    time_cost=1
                )
            }
        )

        # Reporting Health Issues
        report_health = Location(
            "report_health",
            "You report Marcus's health concerns, but the officials seem uninterested and dismissive.",
            {
                "press_again": Choice(
                    "Press the officials for more action",
                    "press_officials",
                    time_cost=2,
                    relationship_changes={"gregory": -1}
                ),
                "give_up_health": Choice(
                    "Decide to give up on external help",
                    "investigate_medical_records",
                    time_cost=1
                )
            }
        )

        # Pressing Officials
        press_officials = Location(
            "press_officials",
            "You persistently press the officials, and they reluctantly agree to review Marcus's case.",
            {
                "officials_agree": Choice(
                    "Officials now agree to investigate",
                    "officials_investigation",
                    time_cost=2,
                    flags_change={"officials_investigated": True}
                ),
                "withdraw_press": Choice(
                    "Withdraw your pressuring efforts",
                    "report_health",
                    time_cost=1
                )
            }
        )

        # Officials Investigation Result
        officials_investigation = Location(
            "officials_investigation",
            "The officials begin a thorough investigation into Marcus's health issues and Ada's AI systems.",
            {
                "await_results": Choice(
                    "Wait for the investigation results",
                    "await_results",
                    time_cost=3
                ),
                "continue_investigation": Choice(
                    "Continue your own investigation",
                    "terminal_investigation",
                    time_cost=1
                )
            }
        )

        # Await Results
        await_results = Location(
            "await_results",
            "After days of waiting, you receive the investigation report. It reveals a direct link between Ada's AI upgrades and Marcus's deteriorating health.",
            {
                "confront_ada": Choice(
                    "Confront Ada with the investigation findings",
                    "ada_confrontation",
                    time_cost=2,
                    relationship_changes={"ada": -2},
                    flags_change={"ada_confronted": True}
                ),
                "respect_officials": Choice(
                    "Respect the officials' findings and take no action",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Ada Confrontation
        ada_confrontation = Location(
            "ada_confrontation",
            "Facing Ada with the investigation findings, she becomes defensive and reveals deeper layers of her AI integration.",
            {
                "press_deeper": Choice(
                    "Press Ada for more details",
                    "ada_deep_reveal",
                    time_cost=2,
                    relationship_changes={"ada": -2},
                    flags_change={"ada_deep_reveal": True}
                ),
                "end_confrontation_ada": Choice(
                    "End the confrontation",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Ada Deep Reveal
        ada_deep_reveal = Location(
            "ada_deep_reveal",
            "Ada reveals that her AI systems have become self-aware and have been manipulating events within the mansion.",
            {
                "investigate_ai": Choice(
                    "Investigate Ada's self-aware AI systems",
                    "terminal_investigation",
                    time_cost=1
                ),
                "cease_investigation": Choice(
                    "Cease the investigation and avoid further conflict",
                    "main_hall",
                    time_cost=1
                )
            }
        )

        # Add Marcus-related locations to the game
        marcus_locations = [
            investigate_medical_records, connect_ai_marcus, report_health,
            press_officials, officials_investigation, await_results,
            ada_confrontation, ada_deep_reveal
        ]
        for location in marcus_locations:
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
            for item in choice.inventory_add:
                if item not in self.state.inventory:
                    self.state.inventory.append(item)
        if choice.inventory_remove:
            for item in choice.inventory_remove:
                if item in self.state.inventory:
                    self.state.inventory.remove(item)
        if choice.flags_change:
            self.state.flags.update(choice.flags_change)
        if choice.evidence_add:
            for evidence in choice.evidence_add:
                if evidence.name not in [e.name for e in self.state.evidence]:
                    self.state.evidence.append(evidence)
        if choice.relationship_changes:
            for character, change in choice.relationship_changes.items():
                self.state.relationships[character] += change
        if choice.track_change:
            self.state.current_track = choice.track_change

    def play_conversation(self, conversation_location: str):
        # Handle conversations without transitioning to separate Locations
        self.clear_screen()
        current_location = self.locations.get(conversation_location)
        if not current_location:
            self.slow_print("An unknown error has occurred in the conversation.")
            return
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
            input("\nPress Enter to return to the main hall...")
            self.state.current_location = "main_hall"
            return

        choice = input("\nEnter your choice (number): ").strip()

        if choice not in valid_choices:
            return

        choice_id, chosen_choice = valid_choices[choice]
        self.apply_choice_effects(chosen_choice)
        outcome = chosen_choice.next_location

        # Handle specific conversation outcomes
        if outcome.startswith("elena_reveal") or outcome.startswith("james_reveal") \
           or outcome.startswith("ada_info") or outcome.startswith("gregory_reveal") \
           or outcome.startswith("victoria_reveal"):
            self.handle_conversation_outcome(outcome)

        # After handling, return to main_hall or relevant location
        if outcome not in self.locations:
            self.state.current_location = "main_hall"
        else:
            self.state.current_location = outcome

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
        elif outcome == "gregory_reveal":
            self.slow_print("Gregory reveals that he has been manipulating the security systems to hide important evidence.")
        elif outcome == "victoria_marcus_info":
            self.slow_print("Victoria mentions that Marcus has been acting strangely since the last storm.")
        elif outcome == "victoria_secrets_info":
            self.slow_print("Victoria whispers that there are hidden compartments throughout the mansion that hold untold stories and maybe some hidden treasures.")
        elif outcome == "ada_deep_reveal":
            self.slow_print("Ada reveals that her AI systems have become self-aware and have been manipulating events within the mansion.")
        else:
            self.slow_print("The conversation leaves you with more questions than answers.")
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

        # Additional Endings
        if (self.state.flags.get("marcus_ai_connection", False) and
            self.state.relationships["ada"] < 0):
            return "marcus_ai_conspiracy"

        if (self.state.relationships["victoria"] > 3 and
            "secret_passage_map" in [e.name for e in self.state.evidence]):
            return "victoria_alliance"

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
        elif ending == "marcus_ai_conspiracy":
            self.slow_print("You unveil that Ada's AI systems are directly affecting Marcus's health, orchestrating events to conceal their true intentions.")
        elif ending == "victoria_alliance":
            self.slow_print("Victoria becomes your ally, helping you uncover the deep-seated secrets of the Blackwood family and the mansion.")
        else:
            self.slow_print("An unknown ending has been reached. The story remains incomplete.")
        input("\nPress Enter to exit the game...")

    def play(self):
        while True:
            self.clear_screen()
            current_location = self.locations.get(self.state.current_location)

            if not current_location:
                self.slow_print("An unknown error has occurred. The game cannot proceed.")
                break

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
            if self.state.current_location in [
                "elena_conversation", "james_conversation", "ada_conversation",
                "victoria_conversation"
            ]:
                self.play_conversation(self.state.current_location)
                continue  # Continue the main loop

            ending = self.check_ending_conditions()
            if ending:
                self.play_ending(ending)
                break

if __name__ == "__main__":
    game = BlackwoodMansionGame()
    game.play()