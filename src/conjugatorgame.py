import logging
import os
import random
import colorama as clr
import contextlib
try:
    import simplejson as json
except ImportError:
    import json


# TODO List
# TODO: Evaluate if cleaning the screen after each try is a better user experience
# TODO: Add a command to exit the app, for instance, write 'exit', or press 'esc'
# TODO: - Add an option to create your own list of verbs.
#       - This option has to be displayed before getting into the temps and mode screen.
#       - Allow saving this list to a file. So users can load it later.
#       - IMPORTANT: This might result in an error, given that we don't have every possible verb
# TODO: We could add a mode in which after some wrong answers, the game ends.


# ---------------------
#  Indicatif
# ---------------------
# "Indicatif Présent", "Indicatif Imparfait", "Indicatif Futur"
# "Indicatif Passé simple", "Indicatif Passé composé", "Indicatif Plus-que-parfait"
# "Indicatif Passé antérieur", "Indicatif Futur antérieur"

# ---------------------
#  Subjonctif
# ---------------------
# "Subjonctif Présent", "Subjonctif Imparfait", "Subjonctif Plus-que-parfait", "Subjonctif Passé"

# ---------------------
#  Conditionnel
# ---------------------
# "Conditionnel Présent", "Conditionnel Passé première forme", "Conditionnel Passé deuxième forme"

# ---------------------
#  Imperatif
# ---------------------
# "Impératif Présent", "Impératif Passé"

logging.basicConfig(level=logging.INFO)

init_msg_special = "\n\n" + \
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

                print('-------------------')
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
                question_text = f"{clr.Style.BRIGHT}mode-temps: {clr.Style.DIM}{verb_time}\n" \
                                f"{clr.Style.BRIGHT}verbe:      {clr.Style.DIM}{verb}\n" \
                                f"{clr.Style.BRIGHT}personne:   {clr.Style.DIM}{person}\n"
                # question_text = f" mode-temps: {clr.Style.BRIGHT}{verb_time}{clr.Style.DIM}\n" \
                #                 f" verbe:      {clr.Style.BRIGHT}{verb}{clr.Style.DIM}\n" \
                #                 f" personne:   {clr.Style.BRIGHT}{person}{clr.Style.DIM}\n"

                raw_input = input(question_text)

                self._evaluate_answer(verb, verb_time, person, raw_input)

                continue_ans = input("\nContinue? [y]/n: ")
                if continue_ans == 'n':
                    self.end_game()

    def end_game(self, error_msg=None):
        self.game_ongoing = False

        if error_msg:
            print(f"An error ocurred:")
            print(error_msg)

        total = self.nb_correct_answers + self.nb_wrong_answers

        print(f"{clr.Style.BRIGHT}")
        #print(" {:^30s}".format("Game finished"))
        print(" {:^30s}".format("Summary"))
        print("-"*30)
        if total:
            # print(f" Correct answers: {self.nb_correct_answers}/{total}")
            # print(f" Score: {100 * self.nb_correct_answers / (total)}")
            print("{:^30}".format(f"Correct answers: {self.nb_correct_answers}/{total}"))
            print("{:^30}".format(f"Score: {100 * self.nb_correct_answers / (total)}"))
        else:
            # print(f" No answers.")
            print("{:^30}".format("No answers"))
        print(f"{clr.Style.RESET_ALL}")


    # -------------------------------------------------------
    #  Helper functions
    # -------------------------------------------------------
    def _evaluate_answer(self, verb, verb_time, person, raw_input):
        raw_input = raw_input.strip()

        if raw_input == "exit":
            self.end_game()
        else:
            if raw_input == self.dictionary[verb][verb_time][person]:
                # clr.Cursor.UP(1)
                self.nb_correct_answers += 1
                print(
                    f"{clr.Style.BRIGHT}{clr.Fore.GREEN}{self.dictionary[verb][verb_time][person]}{clr.Style.RESET_ALL}")
            else:
                self.nb_wrong_answers += 1
                print(
                    f"{clr.Style.BRIGHT}{clr.Fore.RED}{self.dictionary[verb][verb_time][person]}{clr.Style.RESET_ALL}")

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
