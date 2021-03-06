# conj_str = self.dictionary[verb][tense][person]

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
    bs_idx = conj_str[subj_agg_idx+1:].rfind(" ")

    # if not found, try to find an apostrophe
    if bs_idx == -1:
        a_idx = conj_str[subj_agg_idx+1:].rfind("'")

        if a_idx == -1:
            if subj_agg_idx != -1:
                return subj_agg_idx, conj_str[:(subj_agg_idx + 1)]
            else:
                return person_idx, conj_str[:(subj_agg_idx + 1) + (person_idx + 1)]
        else:
            return a_idx, conj_str[:(subj_agg_idx + 1) + (a_idx + 1)]
    else:
        p_idx, _ = get_person_str(None, conj_str[subj_agg_idx+1:subj_agg_idx+1+bs_idx], bs_idx)

    return (subj_agg_idx + 1) + p_idx, conj_str[:(subj_agg_idx + 1) + (p_idx + 1)]

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