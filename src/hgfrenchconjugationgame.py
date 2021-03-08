import logging
import os
import random
import colorama as clr
import shutil
import hgfcgutils
import ctypes

try:
    import simplejson as json
except ImportError:
    import json

logging.basicConfig(level=logging.INFO)


class FrenchConjugationGame:
    DICTIONARIES_REL_PATH = "../res/dictionaries"
    CUSTOM_DICTIONARIES_REL_PATH = "../res/custom_dictionaries"
    PERSONS_IMPERATIVE = ("tu", "nous", "vous")
    PERSONS_REGULAR = ("je", "tu", "il", "elle", "nous", "vous", "ils", "elles")

    def __init__(self):
        # Let's hope this makes colors work on CMD on windows
        clr.init()

        self.dictionary = None
        self.difficult_conjugations = None  # This will be a list with the wrong answers that need to be repeated
        self.game_ongoing = False
        self._indent = 8

        # TODO: Change the negative options once I have everything defined
        self.OPTIONS_DICTIONARY = {1: ["Indicatif Présent", "Indicatif Imparfait", "Indicatif Futur",
                                       "Indicatif Passé simple", "Indicatif Passé composé",
                                       "Indicatif Plus-que-parfait", "Indicatif Passé antérieur",
                                       "Indicatif Futur antérieur"],
                                   11: "Indicatif Présent",
                                   12: "Indicatif Imparfait",
                                   13: "Indicatif Futur",
                                   14: "Indicatif Passé simple",
                                   15: "Indicatif Passé composé",
                                   16: "Indicatif Plus-que-parfait",
                                   17: "Indicatif Passé antérieur",
                                   18: "Indicatif Futur antérieur",
                                   2: ["Subjonctif Présent", "Subjonctif Imparfait", "Subjonctif Plus-que-parfait",
                                       "Subjonctif Passé"],
                                   21: "Subjonctif Présent",
                                   22: "Subjonctif Imparfait",
                                   23: "Subjonctif Plus-que-parfait",
                                   24: "Subjonctif Passé",
                                   3: ["Conditionnel Présent", "Conditionnel Passé première forme",
                                       "Conditionnel Passé deuxième forme"],
                                   31: "Conditionnel Présent",
                                   32: "Conditionnel Passé première forme",
                                   33: "Conditionnel Passé deuxième forme",
                                   4: ["Impératif Présent", "Impératif Passé"],
                                   41: "Impératif Présent",
                                   42: "Impératif Passé",
                                   5: ["Indicatif Présent", "Indicatif Imparfait", "Indicatif Futur",
                                       "Indicatif Passé composé", "Indicatif Plus-que-parfait", "Subjonctif Présent",
                                       "Conditionnel Présent", "Impératif Présent"]
                                   }

        # TODO: Change the negative options once I have everything defined
        self.special_options = [1, 2, 3, 4, 5]
        # self.nb_conjugations = 0
        self.nb_wrong_answers = 0
        self.nb_correct_answers = 0

    def start_app(self):
        # Clear the screen before start
        print(clr.ansi.clear_screen(), end="")

        # Set the title of the app
        print(clr.ansi.set_title("The French Conjugation Game"))

        self._display_options_screen()
        raw_input = input()

        options, error_message = self._process_raw_input_options(raw_input)

        if options is not None:
            if len(options) > 0:
                msg = f"You selected: {list(options)}. Is this OK? [y]/n: "
                # hgfcgutils.print_centered_msg(f"{msg:<{len(msg) + 1}}", end='', place_cursor=True)
                hgfcgutils.print_centered_msg_better(msg, end="")

                confirmation = input()

                if confirmation != "n":
                    self.start_game(options)
        else:
            print(error_message)

    def start_game(self, options):
        verb_times_list = self._create_options_list(options)

        # Load the dictionary into memory. If this fails, it will end the game automatically
        self._load_dictionary()

        if self.dictionary is not None:
            self.game_ongoing = True
            verb_list = list(self.dictionary.keys())

            while self.game_ongoing:
                verb, verb_time, person = self._get_components_question(verb_list, verb_times_list)

                self._display_question_screen(person, verb, verb_time)

                # Display the person, so the user focuses only in conjugating the verb
                _, p_str = hgfcgutils.get_person_str(verb_time, self.dictionary[verb][verb_time][person])
                # raw_input = input(f"{' ' * self._indent}{p_str}")

                # msg = f"{p_str:<{len(self.dictionary[verb][verb_time][person])}}"

                # msg = self.dictionary[verb][verb_time][person]
                # hgfcgutils.prepare_cursor_forward_centered_text(msg)
                # print(p_str, end="")
                hgfcgutils.print_centered_msg_better(p_str,
                                                     msg_len=len(self.dictionary[verb][verb_time][person]),
                                                     end="")

                # hgfcgutils.print_centered_msg(msg, end='', place_cursor=True, cursor_offset=len(p_str))

                # msg = f"{self.dictionary[verb][verb_time][person]:<{len(self.dictionary[verb][verb_time][person])+1}}"
                # hgfcgutils.print_centered_msg(msg, end='')
                raw_input = input()

                self._evaluate_answer(verb, verb_time, person, raw_input, p_str)

    def end_game(self, preamble=None, error_msg=None):
        self.game_ongoing = False
        self._display_end_screen(preamble=preamble, error_msg=error_msg)

    # -------------------------------------------------------
    #  Helper functions
    # -------------------------------------------------------
    def _display_options_screen(self):
        col1_w = 35
        col2_w = 35
        col3_w = 36

        #
        #  Code for left-aligned text
        # -------------------------------------------------------------
        # print(f"{' ' * self._indent}{'-' * 80}\n")
        # print(f"{' ' * self._indent}The French Conjugation Game\n")
        # print(f"{' ' * self._indent}{'-' * 80}\n")

        # print(
        #     f"{' ' * self._indent}Select one of the general options (single digit option) or build your own set using\n"
        #     f"{' ' * self._indent}the individual tenses (double digit option) separated by commas.\n"
        #     #f"{' ' * self._indent}\n"
        # )

        # static_opts_list_str = "\n" \
        #                        f"{' ' * self._indent}{'1 Tous les Indicatifs':<{col1_w}} {'2 Tous les Subjonctifs':<{col2_w}} {'3 Tous les Conditionnels':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'11 {self.OPTIONS_DICTIONARY[11]}':<{col1_w}} {f'21 {self.OPTIONS_DICTIONARY[21]}':<{col2_w}} {f'31 {self.OPTIONS_DICTIONARY[31]}':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'12 {self.OPTIONS_DICTIONARY[12]}':<{col1_w}} {f'22 {self.OPTIONS_DICTIONARY[22]}':<{col2_w}} {f'32 {self.OPTIONS_DICTIONARY[32]}':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'13 {self.OPTIONS_DICTIONARY[13]}':<{col1_w}} {f'23 {self.OPTIONS_DICTIONARY[23]}':<{col2_w}} {f'33 {self.OPTIONS_DICTIONARY[33]}':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'14 {self.OPTIONS_DICTIONARY[14]}':<{col1_w}} {f'24 {self.OPTIONS_DICTIONARY[24]}':<{col2_w}} {f'':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'15 {self.OPTIONS_DICTIONARY[15]}':<{col1_w}} {f'':<{col2_w}} {f'4 Tous les Impératifs':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'16 {self.OPTIONS_DICTIONARY[16]}':<{col1_w}} {f'':<{col2_w}} {f'41 {self.OPTIONS_DICTIONARY[41]}':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'17 {self.OPTIONS_DICTIONARY[17]}':<{col1_w}} {f'':<{col2_w}} {f'42 {self.OPTIONS_DICTIONARY[42]}':<{col3_w}}\n" \
        #                        f"{' ' * self._indent}{f'18 {self.OPTIONS_DICTIONARY[18]}':<{col1_w}} {f'':<{col2_w}} {f'':<{col3_w}}\n\n"
        # custom_opts_str = f"{' ' * self._indent}5. HG selection\n"
        #
        # print(static_opts_list_str)
        # print(f"{' ' * (self._indent-4)}Your selection: ", end='')

        #
        #  Code for center-aligned text
        # -------------------------------------------------------------
        hgfcgutils.print_centered_hline(w_pcnt_screen=0.5, above_space=1, below_space=1)
        hgfcgutils.print_centered_msg("The French Conjugation Game")
        hgfcgutils.print_centered_hline(w_pcnt_screen=0.5, above_space=1, below_space=1)

        instructions_msg_pt1 = "Select one of the general options (single digit option) or build your own set using"
        instructions_msg_pt2 = "the individual tenses (double digit option) separated by commas."

        hgfcgutils.print_centered_msg(instructions_msg_pt1)
        hgfcgutils.print_centered_msg(instructions_msg_pt2)

        print("\n")

        hgfcgutils.print_centered_msg(f"{'1 Tous les Indicatifs':<{col1_w}} "
                                      f"{'2 Tous les Subjonctifs':<{col2_w}} "
                                      f"{'3 Tous les Conditionnels':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'11 {self.OPTIONS_DICTIONARY[11]}':<{col1_w}} "
                                      f"{f'21 {self.OPTIONS_DICTIONARY[21]}':<{col2_w}} "
                                      f"{f'31 {self.OPTIONS_DICTIONARY[31]}':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'12 {self.OPTIONS_DICTIONARY[12]}':<{col1_w}} "
                                      f"{f'22 {self.OPTIONS_DICTIONARY[22]}':<{col2_w}} "
                                      f"{f'32 {self.OPTIONS_DICTIONARY[32]}':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'13 {self.OPTIONS_DICTIONARY[13]}':<{col1_w}} "
                                      f"{f'23 {self.OPTIONS_DICTIONARY[23]}':<{col2_w}} "
                                      f"{f'33 {self.OPTIONS_DICTIONARY[33]}':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'14 {self.OPTIONS_DICTIONARY[14]}':<{col1_w}} "
                                      f"{f'24 {self.OPTIONS_DICTIONARY[24]}':<{col2_w}} "
                                      f"{f'':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'15 {self.OPTIONS_DICTIONARY[15]}':<{col1_w}} "
                                      f"{f'':<{col2_w}} "
                                      f"{f'4 Tous les Impératifs':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'16 {self.OPTIONS_DICTIONARY[16]}':<{col1_w}} "
                                      f"{f'':<{col2_w}} "
                                      f"{f'41 {self.OPTIONS_DICTIONARY[41]}':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'17 {self.OPTIONS_DICTIONARY[17]}':<{col1_w}} "
                                      f"{f'':<{col2_w}} "
                                      f"{f'42 {self.OPTIONS_DICTIONARY[42]}':<{col3_w}}")
        hgfcgutils.print_centered_msg(f"{f'18 {self.OPTIONS_DICTIONARY[18]}':<{col1_w}} "
                                      f"{f'':<{col2_w}} "
                                      f"{f'':<{col3_w}}")

        print("\n")

        hgfcgutils.print_centered_msg(f"{f'5 HG Selection':<{col1_w}} {f'':<{col2_w}} {f'':<{col3_w}}")

        print("\n")

        input_msg = f"Your selection: "
        space_for_options = 6
        # hgfcgutils.print_centered_msg(f"{input_msg:<{len(input_msg) + 1}}", end='', place_cursor=True)
        hgfcgutils.print_centered_msg_better(input_msg, msg_len=len(input_msg) + space_for_options, end="")

        # input_msg = f"{f'Your selection: ':<{col1_w}}"
        # hgfcgutils.print_centered_msg(input_msg, end='')

        # sh_w, sh_h = shutil.get_terminal_size()

        # print(clr.ansi.Cursor.BACK((sh_w // 2) - (len(input_msg) // 2) + (input_msg.rfind(":")) ), end="")

        # hgfcgutils.input_centered_msg(f"{f'Your seletion: ':<{col1_w}}")

        # class COORD(ctypes.Structure):
        #     pass
        #
        # COORD._fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
        #
        # sh_w, sh_h = shutil.get_terminal_size()
        #
        # STD_OUTPUT_HANDLE = -11
        # r = 20
        # c = (sh_w // 2) + 3
        # h = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        # ctypes.windll.kernel32.SetConsoleCursorPosition(h, COORD(c, r))

        # cursor = clr.Cursor.POS((sh_w // 2) + 3, 19)
        # print(clr.Cursor.POS((sh_w // 2) + 3, 20), end='')
        #
        # -------------------------------------------------------------

    def _display_question_screen(self, person, verb, verb_time):
        print(clr.ansi.clear_screen(), end="")

        # Add some vertical space
        # print("\n\n")
        #
        # print(f"{' ' * (self._indent - 1)}{'-' * 40}\n")
        #
        # question_text = f"{' ' * self._indent}{clr.Style.BRIGHT}personne:   {clr.Style.DIM}{person}\n" \
        #                 f"{' ' * self._indent}{clr.Style.BRIGHT}verbe:      {clr.Style.DIM}{verb}\n" \
        #                 f"{' ' * self._indent}{clr.Style.BRIGHT}mode-temps: {clr.Style.DIM}{verb_time}\n"
        #
        # print(question_text)
        #
        # print(f"{' ' * (self._indent - 1)}{'-' * 40}\n")

        #
        #  Code for center-aligned text
        # -------------------------------------------------------------
        box_w = 60
        hline = '-' * box_w
        print("\n")
        hgfcgutils.print_centered_msg(f"{hline:<{box_w}}", end="\n\n")

        person_part = f" personne:   {person}"
        verb_part = f" verbe:      {verb}"
        tense_part = f" mode-temps: {verb_time}"

        hgfcgutils.print_centered_msg(f"{person_part:<{box_w // 2}}")
        hgfcgutils.print_centered_msg(f"{verb_part:<{box_w // 2}}")
        hgfcgutils.print_centered_msg(f"{tense_part:<{box_w // 2}}", end="\n\n")

        hgfcgutils.print_centered_msg(f"{hline:<{box_w}}")
        #
        # -------------------------------------------------------------

    def _display_end_screen(self, preamble=None, error_msg=None):
        print(clr.ansi.clear_screen(), end="")

        # Add some vertical space
        print("\n\n")

        if error_msg:
            hgfcgutils.print_centered_msg("An error ocurred:")
            hgfcgutils.print_centered_msg(error_msg)

        total = self.nb_correct_answers + self.nb_wrong_answers

        print(f"{clr.Style.BRIGHT}", end="")

        if preamble:
            hgfcgutils.print_centered_msg(f"{preamble}\n")

        hgfcgutils.print_centered_msg('Summary')

        hgfcgutils.print_centered_hline(w_pcnt_screen=0.5)

        if total:
            hgfcgutils.print_centered_msg(f'Correct answers: {self.nb_correct_answers}/{total}')
            hgfcgutils.print_centered_msg(f'Score: {100 * self.nb_correct_answers / (total)}')
        else:
            hgfcgutils.print_centered_msg("No answers")

        print(f"{clr.Style.RESET_ALL}", end="")

        hgfcgutils.print_centered_hline(w_pcnt_screen=0.5)
        # hgfcgutils.print_centered_msg("Press [enter] to quit.", end="", place_cursor=True)
        hgfcgutils.print_centered_msg_better("Press [enter] to quit.", end="")

        # Wait for an input to finish the game and clear the screen before getting out of the app
        input()
        print(clr.ansi.clear_screen(), "")

    def _evaluate_answer(self, verb, verb_time, person, raw_input, person_str=""):

        raw_input = raw_input.strip()

        if raw_input == "exit":
            self.end_game("You exit the game")
        else:
            raw_input = f"{person_str}{raw_input}"
            symbol = ""

            if raw_input == self.dictionary[verb][verb_time][person]:
                self.nb_correct_answers += 1
                print(f"{clr.Style.BRIGHT}{clr.Fore.GREEN}", end="")
                symbol = "\u2713"
            else:
                self.nb_wrong_answers += 1
                print(f"{clr.Style.BRIGHT}{clr.Fore.RED}", end="")
                symbol = "\u2717"

            # hgfcgutils.print_centered_msg(f"{self.dictionary[verb][verb_time][person]}", end='', place_cursor=True)
            hgfcgutils.print_centered_msg_better(self.dictionary[verb][verb_time][person], end="")
            print(f" {symbol}")

            print(f"{clr.Style.RESET_ALL}", end="")

            if self.nb_wrong_answers > 4:
                # Wait for an input to take a look at the correct response of the final try.
                print(f"{clr.Style.BRIGHT}", end="")
                # hgfcgutils.print_centered_msg(f"{' ' * self._indent}You ran out of tries. Press [enter] to continue.")
                # hgfcgutils.print_centered_msg("You ran out of tries. Press [enter] to continue.", end='', place_cursor=True)
                hgfcgutils.print_centered_msg_better("You ran out of tries. Press [enter] to continue.", end='')
                print(f"{clr.Style.RESET_ALL}", end="")

                input()
                self.end_game(preamble="You're almost there. Keep practicing!")
            else:
                # continue_ans = input(f"\n{' ' * self._indent}Continue? [y]/n: ")
                # hgfcgutils.print_centered_msg("Continue? [y]/n: ", end='', place_cursor=True)
                hgfcgutils.print_centered_msg_better("Continue? [y]/n: ", end='')
                continue_ans = input()

                if continue_ans == 'n':
                    self.end_game()

    def _get_components_question(self, verb_list, verb_times_list):
        verb = random.choice(verb_list)
        verb_time = random.choice(verb_times_list)

        if verb_time.startswith("Impératif"):
            person = random.choice(self.PERSONS_IMPERATIVE)
        else:
            person = random.choice(self.PERSONS_REGULAR)

        return verb, verb_time, person

    def _load_dictionary(self):
        # Prefer custom dictionaries if there are any
        if hgfcgutils.is_any_file_in_dir(self.CUSTOM_DICTIONARIES_REL_PATH):
            for dir_entry in os.scandir(self.CUSTOM_DICTIONARIES_REL_PATH):
                self._append_dictionary(dir_entry)
        else:
            for dir_entry in os.scandir(self.DICTIONARIES_REL_PATH):
                self._append_dictionary(dir_entry)

        if self.dictionary is None:
            logging.critical("Cannot load the dictionary. Closing.")
            error_msg = "Error. Cannot load the dictionary."
            self.end_game(error_msg)

    def _append_dictionary(self, dir_entry):
        if dir_entry.is_file():
            with open(dir_entry, "r") as f:
                tmp_dict = json.load(f)

                if tmp_dict is None:
                    logging.critical(f"Couldn't load the dictionary: {f}.")
                else:
                    if self.dictionary is None:
                        self.dictionary = dict()
                        self.dictionary.update(tmp_dict)
                    else:
                        self.dictionary.update(tmp_dict)

    def _process_raw_input_options(self, raw_input):
        processed_opts = None
        error_msg = None

        # Prevent trolling
        if len(raw_input) > 20:
            error_msg = "Too much options"

        elif len(raw_input) > 0:
            # Special options: those that are preselected
            opts_list = raw_input.split(",")
            opts_set = set()

            for opt in opts_list:
                try:
                    opt_int = int(opt.strip())
                except:
                    error_msg = f"Not among the integer options: {opt}"
                    break

                if opt_int not in self.OPTIONS_DICTIONARY.keys():
                    error_msg = f"Not among the options: {opt}"
                    break

                opts_set.add(opt_int)

            if error_msg is None:
                processed_opts = opts_set

        return processed_opts, error_msg

    def _create_options_list(self, options):
        final_options = None

        logging.info("searching for special options")

        # If find a special option in 'opts', then we have our list
        for sp_opt in self.special_options:
            if sp_opt in options:
                final_options = self.OPTIONS_DICTIONARY[sp_opt]
                break

        # If 'final_options' is None, we have a user defined set of options. Then, construct the list.
        if final_options is None:
            final_options = list()
            for opt in options:
                final_options.append(self.OPTIONS_DICTIONARY[opt])

        logging.info(final_options)
        return final_options
