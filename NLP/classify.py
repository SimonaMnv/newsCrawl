from elasticsearchapp.query_results import get_all_analyzed_data
import pandas as pd

tokenized_data, raw_type = get_all_analyzed_data()


def export_dataset_df():
    total_data = []
    total_types = []

    for data, type in zip(tokenized_data, raw_type):
        total_data.append(data)
        total_types.append(type)

    print(total_data)
    print(total_types)

    df = pd.DataFrame({'article_tokens': total_data, 'crime_type': total_types})
    df.to_csv('../dfs/newsbomb_article.csv', encoding='utf-8-sig', index=False)

export_dataset_df()