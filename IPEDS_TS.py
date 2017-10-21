import csv
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


def fix_cip_family(x):
    if len(str(x['cipfamily'])) == 1:
        return "0{0}".format(str(x['cipfamily']))
    elif len(str(x['cipfamily'])) == 2:
        return str(x['cipfamily'])


def extract_cipfamily(x):
    item = str(x['cip2010']).split('.')[0]
    if len(item) == 1:
        return "0{0}".format(item)
    else:
        return str(item)


def fix_cipcode_int(x):
    if len(str(x['cipcode'])) == 5:
        return float("{0}.{1}".format(str(x['cipcode'])[0], str(x['cipcode'])[1:]))
    elif len(str(x['cipcode'])) == 6:
        return float("{0}.{1}".format(str(x['cipcode'])[:2], str(x['cipcode'])[1:]))


def fix_cipcode_float(x):
    if len(str(x['cipcode'])) == 6:
        return float("{0}".format(str(x['cipcode'])))
    elif len(str(x['cipcode'])) == 7:
        return float(x['cipcode'])


def fix_award_level(x):
    if int(x['awlevel']) == 3:
        return "Associate's degree"
    if int(x['awlevel']) == 5:
        return "Bachelor's degree"
    if int(x['awlevel']) == 7:
        return "Master's degree"
    if int(x['awlevel']) == 17:
        return "Doctor's degree - research/scholarship"
    if int(x['awlevel']) == 18:
        return "Doctor's degree - professional practice"
    if int(x['awlevel']) == 19:
        return "Doctor's degree - other"
    if int(x['awlevel']) == 1:
        return "Award of less than 1 academic year"
    if int(x['awlevel']) == 2:
        return "Award of at least 1 but less than 2 academic years"
    if int(x['awlevel']) == 4:
        return "Award of at least 2 but less than 4 academic years"
    if int(x['awlevel']) == 6:
        return "Postbaccalaureate certificate"
    if int(x['awlevel']) == 8:
        return "Post-master's certificate"


#TODO INVOKE CROSSWALK

def get_everything():
    category_reference_df = pd.DataFrame.from_csv("reference/CategoryReference.csv", index_col=None)
    category_reference_df['cipfamily'] = category_reference_df.apply(fix_cip_family, axis=1)

    fine_reference_df = pd.DataFrame.from_csv("reference/FineReference.csv", index_col=None)

    cip_1985_to_2010_df = pd.DataFrame.from_csv("reference/Crosswalk1985to2010.csv", index_col=None)
    cip_1990_to_2010_df = pd.DataFrame.from_csv("reference/Crosswalk1990to2010.csv", index_col=None)
    cip_2000_to_2010_df = pd.DataFrame.from_csv("reference/Crosswalk2000to2010.csv", index_col=None)

    with open("total.csv", "wb") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=
        ['year',
         'cipfamily',
         'cipfamilytitle',
         'cip2010',
         'ciptitle2010',
         'award_level',
         'men',
         'women',
         'white_men',
         'white_women',
         'latin_hispanic_men',
         'latin_hispanic_women',
         'black_men',
         'black_women',
         'asian_men',
         'asian_women',
         'international_men',
         'international_women',
         'native_american_men',
         'native_american_women',
         'hawaiian_pacific_men',
         'hawaiian_pacific_women',
         'multiracial_men',
         'multiracial_women',
         'unknown_men',
         'unknown_women',
        "isSTEM",
        "isLiberalArt",
        "isHealthMedical",
        "isEducation",
        "isBusiness",
        "isLawPublicSocialService",
        "isMedia",
        "isVocationalTechnical",
        "isBasic",
        "isSTEAM"
         ])
        writer.writeheader()

        for year, completion_file in get_completions():
            if year != "1984":
            # if int(year) >= 2011:
                completion_df = pd.DataFrame.from_csv(os.path.join("completions", completion_file), index_col=None)
                completion_df.columns = map(str.lower, completion_df.columns)
                completion_df.columns = map(str.strip, completion_df.columns)
                print year, completion_file
                print completion_df.columns

                completion_df['awlevel'] = completion_df.apply(fix_award_level, axis=1)

                if completion_df['cipcode'].dtype == np.int64:
                    completion_df['cipcode'] = completion_df.apply(fix_cipcode_int, axis=1)
                elif completion_df['cipcode'].dtype == np.float64:
                    completion_df['cipcode'] = completion_df.apply(fix_cipcode_float, axis=1)

                if 1985 <= int(year) < 1990:
                    completion_df = completion_df.merge(cip_1985_to_2010_df, how="left", on='cipcode')
                    completion_df = completion_df.drop('cipcode', axis=1)
                elif 1990 <= int(year) < 2000:
                    completion_df = completion_df.merge(cip_1990_to_2010_df, how="left", on='cipcode')
                    completion_df = completion_df.drop('cipcode', axis=1)
                elif 2000 <= int(year) < 2010:
                    completion_df = completion_df.merge(cip_2000_to_2010_df, how="left", on='cipcode')
                    completion_df = completion_df.drop('cipcode', axis=1)
                else:
                    completion_df['cip2010'] = completion_df['cipcode']
                    completion_df = completion_df.drop('cipcode', axis=1)

                completion_df['cipfamily'] = completion_df.apply(extract_cipfamily, axis=1)
                completion_df = completion_df.merge(category_reference_df, how="left", on='cipfamily')
                completion_df = completion_df.merge(fine_reference_df, how="left", on='cip2010')

                completion_df = completion_df[completion_df.cipfamily != '99']

                for key, group in completion_df.groupby(['cip2010', 'awlevel']):

                    result_dict = {}
                    result_dict['year'] = year
                    result_dict['cip2010'] = key[0]
                    result_dict['ciptitle2010'] = group['ciptitle2010'].iloc[0]
                    result_dict['award_level'] = key[1]
                    result_dict['cipfamily'] = group['cipfamily'].iloc[0]
                    result_dict['cipfamilytitle'] = group['cipfamilytitle'].iloc[0]
                    result_dict['isSTEM'] = group['isSTEM'].iloc[0]
                    result_dict['isLiberalArt'] = group['isLiberalArt'].iloc[0]
                    result_dict['isHealthMedical'] = group['isHealthMedical'].iloc[0]
                    result_dict['isEducation'] = group['isEducation'].iloc[0]
                    result_dict['isBusiness'] = group['isBusiness'].iloc[0]
                    result_dict['isLawPublicSocialService'] = group['isLawPublicSocialService'].iloc[0]
                    result_dict['isMedia'] = group['isMedia'].iloc[0]
                    result_dict['isVocationalTechnical'] = group['isVocationalTechnical'].iloc[0]
                    result_dict['isBasic'] = group['isBasic'].iloc[0]
                    result_dict['isSTEAM'] = group['isSTEAM'].iloc[0]

                    if "ctotalt" in completion_df.columns:
                        result_dict["men"] = group['ctotalm'].sum()
                        result_dict["women"] = group['ctotalw'].sum()
                        result_dict["white_men"] = group['cwhitm'].sum()
                        result_dict["white_women"] = group['cwhitw'].sum()
                        result_dict["latin_hispanic_men"] = group['chispm'].sum()
                        result_dict["latin_hispanic_women"] = group['chispw'].sum()
                        result_dict["black_men"] = group['cbkaam'].sum()
                        result_dict["black_women"] = group['cbkaaw'].sum()
                        result_dict["asian_men"] = group['casiam'].sum()
                        result_dict["asian_women"] = group['casiaw'].sum()
                        result_dict["international_men"] = group['cnralm'].sum()
                        result_dict["international_women"] = group['cnralw'].sum()
                        result_dict["native_american_men"] = group['caianm'].sum()
                        result_dict["native_american_women"] = group['caianw'].sum()
                        result_dict["hawaiian_pacific_men"] = group['cnhpim'].sum()
                        result_dict["hawaiian_pacific_women"] = group['cnhpiw'].sum()
                        result_dict["multiracial_men"] = group['c2morm'].sum()
                        result_dict["multiracial_women"] = group['c2morw'].sum()
                        result_dict["unknown_men"] = group['cunknm'].sum()
                        result_dict["unknown_women"] = group['cunknw'].sum()

                    elif 'crace15' in completion_df.columns:
                        result_dict["men"] = group['crace15'].sum()
                        result_dict["women"] = group['crace16'].sum()
                        if 'crace01' in completion_df.columns:
                            result_dict["white_men"] = group['crace11'].sum()
                            result_dict["white_women"] = group['crace12'].sum()
                            result_dict["latin_hispanic_men"] = group['crace09'].sum()
                            result_dict["latin_hispanic_women"] = group['crace10'].sum()
                            result_dict["black_men"] = group['crace03'].sum()
                            result_dict["black_women"] = group['crace04'].sum()
                            result_dict["asian_men"] = group['crace07'].sum()
                            result_dict["asian_women"] = group['crace08'].sum()
                            result_dict["international_men"] = group['crace01'].sum()
                            result_dict["international_women"] = group['crace02'].sum()
                            result_dict["native_american_men"] = group['crace05'].sum()
                            result_dict["native_american_women"] = group['crace06'].sum()
                            result_dict["unknown_men"] = group['crace13'].sum()
                            result_dict["unknown_women"] = group['crace14'].sum()
                    writer.writerow(result_dict)


# TODO: FUNCTIONS FOR TOTAL AND GENDER BY DISCIPLINE AND DEGREE LEVEL

#TODO: FUNCTIONS FOR RACIAL DIVERSITY, TOTAL
#TODO: FUNCTIONS FOR RACIAL DIVERSITY BY DISCIPLINE AND DEGREE LEVEL

def main():
    get_everything()

    return


if __name__ == "__main__":
    main()