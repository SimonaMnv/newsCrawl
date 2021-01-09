from elasticsearchapp.query_results import analyzed_results_body, analyzed_results_title, analyzed_results_tags


def create_ds():
    ds = []

    bodies = analyzed_results_body()
    print(bodies)

    titles = analyzed_results_title()
    print(titles)

    tags = analyzed_results_tags()
    print(tags)

    return ds

create_ds()