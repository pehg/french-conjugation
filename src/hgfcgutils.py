import shutil
import os
import contextlib


# ---------------------------------------------------------------------------------------------------------------------
#  Directory functions
# ---------------------------------------------------------------------------------------------------------------------
@contextlib.contextmanager
def change_dir(directory):
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


# ---------------------------------------------------------------------------------------------------------------------
#  Centered print functions
# ---------------------------------------------------------------------------------------------------------------------
def get_person_str(tense, conj_str, person_idx=0):
    subj_agg_idx = -1

    if tense is not None:
        if tense.startswith("Sub"):
            # Subjunctive start with "que" or "qu'", we can remove this part and add it later
            # Add 1 here so we can declare subj_agg_idx as 0. Just avoid an extra operation everytime subj_agg_idx is
            # used.
            subj_ap_idx = conj_str.find("'")
            sub_bs_idx = conj_str.find(" ")

            if sub_bs_idx != -1 and subj_ap_idx != -1:
                subj_agg_idx = min(sub_bs_idx, subj_ap_idx)
            else:
                subj_agg_idx = max(sub_bs_idx, subj_ap_idx)
        # Imperative doesn't have pronoun
        elif tense.startswith("Imp"):
            return -1, ""

    # Always try to find the last blank space
    bs_idx = conj_str[subj_agg_idx + 1:].rfind(" ")

    # if not found, try to find an apostrophe
    if bs_idx == -1:
        a_idx = conj_str[subj_agg_idx + 1:].rfind("'")

        if a_idx == -1:
            if subj_agg_idx != -1:
                return subj_agg_idx, conj_str[:(subj_agg_idx + 1)]
            else:
                return person_idx, conj_str[:(subj_agg_idx + 1) + (person_idx + 1)]
        else:
            return a_idx, conj_str[:(subj_agg_idx + 1) + (a_idx + 1)]
    else:
        p_idx, _ = get_person_str(None, conj_str[subj_agg_idx + 1:subj_agg_idx + 1 + bs_idx], bs_idx)

    return (subj_agg_idx + 1) + p_idx, conj_str[:(subj_agg_idx + 1) + (p_idx + 1)]


# ---------------------------------------------------------------------------------------------------------------------
#  Centered print functions
# ---------------------------------------------------------------------------------------------------------------------
def print_centered_hline(pattern='-', w_pcnt_screen=1.0, above_space=0, below_space=0):
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


def print_centered_msg(msg, downsize=0):
    # Request the size of the shell everytime just in case the user resized in the middle of the game
    sh_w, sh_h = shutil.get_terminal_size()

    print(f"{msg:^{sh_w}}")

# TODO: Turn this into UTs
# Testing my recursive function go extract the index where the person of the verb finishes
# conj_str = "j'étais"
# idx, person = get_person_str("Indicatif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "j'ai dit"
# idx, person = get_person_str("Indicatif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "nous avions dit"
# idx, person = get_person_str("Indicatif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "qu'elle dise"
# idx, person = get_person_str("Subjonctif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "que vous ayez dit"
# idx, person = get_person_str("Subjonctif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "que j'aie dit"
# idx, person = get_person_str("Subjonctif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "qu'il ait dit"
# idx, person = get_person_str("Subjonctif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
#
# conj_str = "ayons eu"
# idx, person = get_person_str("Impératif", conj_str)
# print("-------------------------------------------------")
# print(conj_str)
# print(f"{conj_str[:idx + 1]}     {conj_str[idx + 1:]}")
# print(f"{person}")
