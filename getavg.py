import pandas as pd
from argparse import ArgumentParser


def build_argparser():
    """
    Parse command line arguments.
    :return: command line arguments
    """
    parser = ArgumentParser()
    parser.add_argument("-ind", "--inputdf", required=True, type=str,
                        help="Name of the input csv file.")
    parser.add_argument("-otd", "--outputdf", required=True, type=str,
                        help="Name of the output csv file.")
    return parser


def update_price (x):
    nm = x.replace('$','').replace(',','')
    if '-' in nm:
       nm = abs(float(nm.split('-')[1].strip()) + float(nm.split('-')[0].strip())) / 2.0
       nm = round(nm,2)
    return str(nm)

def get_avgs(args):

    input_df = args.inputdf
    output_df = args.outputdf
    
    kw_df =pd.read_csv(f'{(input_df)}.csv')

    kw_df['price'] = kw_df['price'].astype(str)
    kw_df['price'] = kw_df['price'].apply(update_price)
    kw_df['price'] = kw_df['price'].astype(float)

    nw_df = kw_df.groupby(['keyword','stock']).agg({'price': 'mean', 'stock':'count'})\
                                                    .rename(columns={'stock':'stock_avg', 'price':'price_avg'})\
                                                    .reset_index()

    #pr_df = nw_df.loc[nw_df.groupby('keyword')["price_avg"].idxmax()].reset_index()
    pr_df = nw_df.groupby('keyword')["price_avg"].max().reset_index()
    pr_df['price_avg'] = pr_df['price_avg'].round(2)
    #print(pr_df)
    stk_df = nw_df.groupby('keyword')["stock_avg"].max().reset_index()
    #print(stk_df)
    fnw_df = pd.merge(pr_df, stk_df, on='keyword')

    fnw_df.to_csv(f'{(output_df)}.csv', index=False)
    print('saving is done ')

if __name__ == '__main__':
    args = build_argparser().parse_args()
    get_avgs(args)


