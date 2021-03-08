import shutil
import os
import contextlib
import colorama as clr


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


def is_any_file_in_dir(dir):
    ret = False
    for dir_entry in os.scandir(dir):
        if dir_entry.is_file():
            ret = True
            break

    return ret


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
    print('\n' * above_space, end='')
    print(f"{f'{pattern * line_width}':^{sh_w}}")
    print('\n' * below_space, end='')


def print_centered_msg(msg, end='\n', place_cursor=False, cursor_offset=0):
    # Request the size of the shell everytime just in case the user resized in the middle of the game
    sh_w, sh_h = shutil.get_terminal_size()

    print(f"{msg:^{sh_w}}", end=end)

    if place_cursor:
        print(clr.ansi.Cursor.BACK((sh_w // 2) - (len(msg) // 2) + cursor_offset), end="")


def print_centered_msg_better(msg, msg_len=-1, end="\n", cursor_offset=0):
    """
    Print the string "msg" centered in the current line in the console.

    Args:
        msg (str): String to be printed at the center of the current line in the console.
        msg_len (int, opt): In case that the length of the message is not the same as the space required (can be used to
                            partially write a text that will be filled later but we want the final expression to be
                            centered.
        end (str, opt): Character to print at the end of the message. Passed directly to print()
        cursor_offset (int, opt): Similar to msg_len.

    Returns:
        None

    Notes:
        It assumes that the cursor is positioned at the beginning on the current line.
        I consider this a better version of "print_centered_msg" since it doesn't fill with blanks the right side of the
        text printed, thus, if end="", you can continue writing next to the centered text.
    """
    # Request the size of the shell everytime just in case the user resized in the middle of the game
    sh_w, sh_h = shutil.get_terminal_size()

    # Place the cursor at the correct position to print the centered message
    if msg_len == -1:
        print(clr.ansi.Cursor.FORWARD(int(sh_w / 2 - len(msg) / 2) + cursor_offset), end="")
    else:
        print(clr.ansi.Cursor.FORWARD(int(sh_w / 2 - msg_len / 2) + cursor_offset), end="")

    print(msg, end=end)


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
