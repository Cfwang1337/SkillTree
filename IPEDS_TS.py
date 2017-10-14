import numpy as np
import os
import pandas as pd


def get_completions():
    file_list = []
    for item in os.listdir("completions"):
        if item[-3:] == "csv":
            pre_year = item[1:5]
            if pre_year[0] not in ["1", "2"]:
                year = "19{0}".format(pre_year[2:5])
            else:
                year = pre_year
            file_list.append((year, item))
    return file_list


def fix_cip_int(x):
        if len(str(x['cipcode'])) == 5:
            return "0{0}".format(str(x['cipcode'])[0])
        elif len(str(x['cipcode'])) == 6:
            return str(x['cipcode'])[:2]


def fix_cip_float(x):
        if len(str(x['cipcode'])) == 6:
            return "0{0}".format(str(x['cipcode'])[0])
        elif len(str(x['cipcode'])) == 7:
            return str(x['cipcode'])[:2]


#TODO INVOKE CROSSWALK


#TODO: FUNCTIONS FOR TOTAL AND GENDER BY DISCIPLINE, TOTAL
def total_and_gender():
    for year, completion_file in get_completions():
        completion_df = pd.DataFrame.from_csv(os.path.join("completions", completion_file), index_col=None)
        completion_df['year'] = year
        completion_df.columns = map(str.lower, completion_df.columns)
        print year, completion_file
        # print completion_df.columns

        if completion_df['cipcode'].dtype == np.int64:
            completion_df['cipfamily'] = completion_df.apply(fix_cip_int, axis=1)
        elif completion_df['cipcode'].dtype == np.float64:
            completion_df['cipfamily'] = completion_df.apply(fix_cip_float, axis=1)

        print completion_df['cipcode'][:10]
        print completion_df['cipfamily'][:10]

        #TODO WHAT DO WE GROUP BY?

        #
        # if "ctotalt" in completion_df.columns:
        #     men = "ctotalm"
        #     women = "ctotalw"
        #     total = "ctotalt"
        # elif "crace15" in completion_df.columns:
        #     men = "crace15"
        #     women = "crace16"





# TODO: FUNCTIONS FOR TOTAL AND GENDER BY DISCIPLINE AND DEGREE LEVEL

#TODO: FUNCTIONS FOR RACIAL DIVERSITY, TOTAL
#TODO: FUNCTIONS FOR RACIAL DIVERSITY BY DISCIPLINE AND DEGREE LEVEL

def main():
    print "PLEASE CHOOSE"
    print "0. TOTAL AND GENDER BY DISCIPLINE "
    # print "1. TOTAL RACIAL DIVERSITY "
    # print "2. RACIAL DIVERSITY BY RACE"

    choice = raw_input("ENTER CHOICE: ")

    if choice == "0":
        total_and_gender()
    # elif choice == "1":
    #     analyze_follows()

    return


if __name__ == "__main__":
    main()