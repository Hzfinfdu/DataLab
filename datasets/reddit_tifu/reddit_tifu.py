import json
import os
import datalabs
from datalabs.tasks import Summarization

_DESCRIPTION = """
 Reddit TIFU dataset, consisting of 120K posts from the online discussion forum Reddit
 From paper: "Abstractive Summarization of Reddit Posts with Multi-level Memory Networks" by B. Kim et al.
 See: https://aclanthology.org/N19-1260.pdf
"""
_CITATION = """\
    @inproceedings{kim-etal-2019-abstractive,
    title = "Abstractive Summarization of {R}eddit Posts with Multi-level Memory Networks",
    author = "Kim, Byeongchang  and
      Kim, Hyunwoo  and
      Kim, Gunhee",
    booktitle = "Proceedings of the 2019 Conference of the North {A}merican Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)",
    month = jun,
    year = "2019",
    address = "Minneapolis, Minnesota",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/N19-1260",
    doi = "10.18653/v1/N19-1260",
    pages = "2519--2531",
    abstract = "We address the problem of abstractive summarization in two directions: proposing a novel dataset and a new model. First, we collect Reddit TIFU dataset, consisting of 120K posts from the online discussion forum Reddit. We use such informal crowd-generated posts as text source, in contrast with existing datasets that mostly use formal documents as source such as news articles. Thus, our dataset could less suffer from some biases that key sentences usually located at the beginning of the text and favorable summary candidates are already inside the text in similar forms. Second, we propose a novel abstractive summarization model named multi-level memory networks (MMN), equipped with multi-level memory to store the information of text from different levels of abstraction. With quantitative evaluation and user studies via Amazon Mechanical Turk, we show the Reddit TIFU dataset is highly abstractive and the MMN outperforms the state-of-the-art summarization models.",
}
"""
_ABSTRACT = "summary"
_ARTICLE = "text"

def _gdrive_url(id):
    return f"https://drive.google.com/uc?id={id}&export=download"

class RedditTIFUConfig(datalabs.BuilderConfig):
    """BuilderConfig for RedditTIFU."""

    def __init__(self, **kwargs):
        """BuilderConfig for RedditTIFU.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(RedditTIFUConfig, self).__init__(**kwargs)


class RedditTIFUDataset(datalabs.GeneratorBasedBuilder):
    """RedditTIFU Dataset."""
    _FILE_ID = "1ffWfITKFMJeqjT8loC8aiCLRNJpc_XnF"
    BUILDER_CONFIGS = [
        RedditTIFUConfig(
            name="short",
            version=datalabs.Version("1.0.0"),
            description="RedditTIFU dataset for summarization, short version (using title as summary).",
        ),
        RedditTIFUConfig(
            name="long",
            version=datalabs.Version("1.0.0"),
            description="RedditTIFU dataset for summarization, long version (using tldr as summary).",
        ),
    ]
    DEFAULT_CONFIG_NAME = "long"

    def _info(self):
        # Should return a datalab.DatasetInfo object
        return datalabs.DatasetInfo(
            description=_DESCRIPTION,
            features=datalabs.Features(
                {
                    _ARTICLE: datalabs.Value("string"),
                    _ABSTRACT: datalabs.Value("string"),
                    # "id": datalab.Value("string"),
                }
            ),
            supervised_keys=None,
            homepage=None,
            citation=_CITATION,
            task_templates=[Summarization(
                text_column=_ARTICLE,
                summary_column=_ABSTRACT),
            ],
        )

    def _split_generators(self, dl_manager):
        f_path = dl_manager.download(_gdrive_url(self._FILE_ID))
    
        return [
            datalabs.SplitGenerator(
                name=datalabs.Split.TRAIN, gen_kwargs={"f_path": f_path}
            ),
        ]

    def _generate_examples(self, f_path):
        """Generate RedditTIFU examples."""
        cnt = 0
        with open(f_path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line) 
                if self.config.name == "short":
                    # short version dataset
                    yield cnt, {
                        _ARTICLE: data["selftext_without_tldr"],
                        _ABSTRACT: data["trimmed_title"],
                    }
                    cnt += 1
                elif data["tldr"] is not None:
                    # long version dataset
                    yield cnt, {
                        _ARTICLE: data["selftext_without_tldr"],
                        _ABSTRACT: data["tldr"],
                    }
                    cnt += 1