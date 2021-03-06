import logging
import os
import random
import colorama as clr
import contextlib
import shutil
import hgfcgutils
try:
    import simplejson as json
except ImportError:
    import json

logging.basicConfig(level=logging.INFO)

init_msg_special = "\n" + \
                   "-----------------------------------------------------------------\n" + \
                   "  Conjugaison verbe Français\n" + \
                   "-----------------------------------------------------------------\n" + \
                   " Please select either a special set or build your own:\n" + \
                   "  {:<30s} {:<30s} {:<30s}\n".format("1 Tous les Infinitifs", "2 Tous les Subjonctifs",
                                                        "3 Tous les Conditionnels") + \
                   "  {:<30s} {:<30s} {:<30s}\n".format("11 Indicatif Présent", "21 Subjonctif Présent",
                                                        "31 Conditionnel Présent") + \
                   "  {:<30s} {:<30s} {:<30s}\n".format("12 Indicatif Imparfait", "22 Subjonctif Imparfait",
                                                        "32 Conditionnel Passé première forme") + \
                   "  5. HG selection\n\n" \
                   "Your choice: "


class FrenchConjugatorGame:
    DICTIONARIES_REL_PATH = "../res/dictionaries"
    DICTIONARY_FILENAME = "dictionary-conj-verbs.json"
    PERSONS_IMPERATIVE = ("tu", "nous", "vous")
    PERSONS_REGULAR = ("je", "tu", "il", "elle", "nous", "vous", "ils", "elles")

    def __init__(self):
        # Let's hope this makes colors work on CMD on windows
        clr.init()

        self.dictionary = None
        self.difficult_conjugations = None  # This will be a list with the wrong answers that need to be repeated
        self.game_ongoing = False

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
        print(clr.ansi.clear_screen())

        raw_input = input(init_msg_special)

        options, error_message = self._process_raw_input_options(raw_input)

        if options is not None:
            if len(options) > 0:
                confirmation = input(f"You selected: {options}. Is this OK? [y]/n: ")

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

                print(clr.ansi.clear_screen())

                # print('-------------------')
                self._print_centered_hline(w_pcnt_screen=0.5)
                # question_text = f"{clr.Style.BRIGHT}" \
                #                 f" verbe:      {verb}\n" \
                #                 f" personne:   {person}\n" \
                #                 f" mode-temps: {verb_time}\n" \
                #                 f"{clr.Style.RESET_ALL}"
                #
                # question_text = f" {clr.Style.BRIGHT}verbe:      {clr.Style.DIM}{verb}\n" \
                #                 f" {clr.Style.BRIGHT}personne:   {clr.Style.DIM}{person}\n" \
                #                 f" {clr.Style.BRIGHT}mode-temps: {clr.Style.DIM}{verb_time}\n"
                #
                # question_text = f" verbe:      {clr.Style.BRIGHT}{verb}{clr.Style.DIM}\n" \
                #                 f" personne:   {clr.Style.BRIGHT}{person}{clr.Style.DIM}\n" \
                #                 f" mode-temps: {clr.Style.BRIGHT}{verb_time}{clr.Style.DIM}\n"
                #
                # question_text = f"{clr.Style.BRIGHT}mode-temps: {clr.Style.DIM}{verb_time}\n" \
                #                 f"{clr.Style.BRIGHT}verbe:      {clr.Style.DIM}{verb}\n" \
                #                 f"{clr.Style.BRIGHT}personne:   {clr.Style.DIM}{person}\n"
                #
                # question_text = f" mode-temps: {clr.Style.BRIGHT}{verb_time}{clr.Style.DIM}\n" \
                #                 f" verbe:      {clr.Style.BRIGHT}{verb}{clr.Style.DIM}\n" \
                #                 f" personne:   {clr.Style.BRIGHT}{person}{clr.Style.DIM}\n"

                # print(question_text)

                # self._print_centered_msg(f"{clr.Style.BRIGHT}mode-temps: {clr.Style.DIM}{verb_time}")
                # self._print_centered_msg(f"{clr.Style.BRIGHT}verbe: {clr.Style.DIM}{verb}")
                # self._print_centered_msg(f"{clr.Style.BRIGHT}personne: {clr.Style.DIM}{person}")

                self._print_centered_msg(f"mode-temps: {verb_time}")
                self._print_centered_msg(f"verbe: {verb}")
                self._print_centered_msg(f"personne: {person}")
                # Display the person, so the user focuses only in conjugating the verb
                _, p_str = hgfcgutils.get_person_str(verb_time, self.dictionary[verb][verb_time][person])
                raw_input = input(p_str)

                self._evaluate_answer(verb, verb_time, person, raw_input, p_str)

    def end_game(self, preamble=None, error_msg=None):
        sh_w, sh_h = shutil.get_terminal_size()

        self.game_ongoing = False

        print(clr.ansi.clear_screen())

        if error_msg:
            print(f"An error ocurred:")
            print(error_msg)

        total = self.nb_correct_answers + self.nb_wrong_answers

        print(f"{clr.Style.BRIGHT}")

        if preamble:
            self._print_centered_msg(f"{preamble}\n")

        self._print_centered_msg('Summary')

        self._print_centered_hline(w_pcnt_screen=0.5)

        if total:
            self._print_centered_msg(f'Correct answers: {self.nb_correct_answers}/{total}')
            self._print_centered_msg(f'Score: {100 * self.nb_correct_answers / (total)}')
        else:
            self._print_centered_msg("No answers")
        print(f"{clr.Style.RESET_ALL}")

        # Wait for an input to finish the game and clear the screen before getting out of the app
        input()
        print(clr.ansi.clear_screen())

    # -------------------------------------------------------
    #  Helper functions
    # -------------------------------------------------------
    @staticmethod
    def _print_centered_hline(pattern='-', w_pcnt_screen=1.0, above_space=0, below_space=0):
        if w_pcnt_screen < 0:
            return
        elif w_pcnt_screen > 1:
            w_pcnt_screen = 1

        # TODO: If we have a pattern that consists in more than one character, we have to do a correction. BUt this is
        #       a helper function, it won't be used in a very complicated way.
        len(pattern)

        sh_w, sh_h = shutil.get_terminal_size()

        line_width = int(sh_w * w_pcnt_screen)

        # TODO: pending to make it work
        # print(f"'\n'*above_space"
        #       f"{f'{pattern * line_width}':{sh_w}}"
        #       f"{f'\n' * below_space}")
        print(f"{f'{pattern * line_width}':^{sh_w}}")

    @staticmethod
    def _print_centered_msg(msg, downsize=0):
        # Request the size of the shell everytime just in case the user resized in the middle of the game
        sh_w, sh_h = shutil.get_terminal_size()

        print(f"{msg:^{sh_w}}")

    def _evaluate_answer(self, verb, verb_time, person, raw_input, person_str=""):

        raw_input = raw_input.strip()

        if raw_input == "exit":
            self.end_game("You exit the game.")
        else:
            raw_input = f"{person_str}{raw_input}"
            if raw_input == self.dictionary[verb][verb_time][person]:
                self.nb_correct_answers += 1
                print(
                    f"{clr.Style.BRIGHT}{clr.Fore.GREEN}{self.dictionary[verb][verb_time][person]}{clr.Style.RESET_ALL}")
            else:
                self.nb_wrong_answers += 1
                print(
                    f"{clr.Style.BRIGHT}{clr.Fore.RED}{self.dictionary[verb][verb_time][person]}{clr.Style.RESET_ALL}")

            if self.nb_wrong_answers > 4:
                # Wait for an input to take a look at the correct response of the final try.
                # print(f"{clr.Style.BRIGHT}\nYou ran out of tries. Press [enter] to continue.{clr.Style.DIM}")
                self._print_centered_msg(f"{clr.Style.BRIGHT}\nYou ran out of tries. Press [enter] to continue.{clr.Style.DIM}")
                input()
                self.end_game(preamble="You're almost there. Keep practicing!")
            else:
                continue_ans = input("\nContinue? [y]/n: ")
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

        with self._change_dir(self.DICTIONARIES_REL_PATH):
            for file in os.listdir():
                with open(file, "r") as f:
                    tmp_dict = json.load(f)

                    if tmp_dict is None:
                        logging.critical(f"Couldn't load the dictionary: {file}.")
                    else:
                        if self.dictionary is None:
                            self.dictionary = dict()
                            self.dictionary.update(tmp_dict)
                        else:
                            self.dictionary.update(tmp_dict)

        if self.dictionary is None:
            logging.critical("Cannot load the dictionary. Closing.")
            error_msg = "Error. Cannot load the dictionary."
            self.end_game(error_msg)
        # else:
        #     verb_list = list(self.dictionary.keys())

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

    @contextlib.contextmanager
    def _change_dir(self, directory):
        """
        Changes directory. Should be static but not sure if

        Args:
            directory (str): Directory to change to.

        Returns:

        """
        saved_dir = os.getcwd()
        os.chdir(directory)

        yield

        os.chdir(saved_dir)
