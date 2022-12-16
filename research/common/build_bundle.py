import math
import typing as tp
from pathlib import Path

import pandas as pd
import yo_fluq_ds as yfds

from tg.grammar_ru.common import Loc

from tg.grammar_ru.ml.features import PyMorphyFeaturizer, SlovnetFeaturizer, SyntaxTreeFeaturizer, SyntaxStatsFeaturizer
from tg.grammar_ru.ml.corpus import CorpusReader, CorpusBuilder, BucketCorpusBalancer

from tg.grammar_ru.ml.tasks.train_index_builder.index_builders import IndexBuilder
from tg.grammar_ru.ml.tasks.train_index_builder.sentence_filterer import SentenceFilterer


def balance(
        filtered_corpuses: tp.List[Path],
        bucket_path: Path,
        balanced_corpus_path: Path,
        bucket_numbers: tp.List[int],
        bucket_limit: int
        ) -> None:
    BucketCorpusBalancer.build_buckets_frame(filtered_corpuses, bucket_path)

    balancer = BucketCorpusBalancer(
        buckets=pd.read_parquet(bucket_path),
        log_base=math.e,
        bucket_limit=bucket_limit,
    )

    CorpusBuilder.transfuse_corpus(
        sources=filtered_corpuses,
        destination=balanced_corpus_path,
        selector=balancer
    )


def read_data(corpus_path: Path) -> tp.Iterable[pd.DataFrame]:
    return (CorpusReader(corpus_path)
            .get_frames()
            .feed(yfds.fluq.with_progress_bar()))


def filter_corpuses(
        filterer: SentenceFilterer,
        corpuses: tp.List[Path],
        word_limit: tp.Optional[int] = None
        ) -> None:
    for corpus_path in corpuses:
        corpus_name = corpus_path.name.split('.')[0]
        filtered_path = Loc.bundles_path/f'chtoby/filtered_{corpus_name}'
        print(corpus_path)
        print(filtered_path)

        CorpusBuilder.transfuse_corpus(
            [corpus_path],
            filtered_path,
            selector=filterer
        )


def build_index(
        index_builder: IndexBuilder,
        corpus_path: Path,
        bundle_path: Path,
        word_limit: tp.Optional[int] = None
        ) -> None:
    CorpusBuilder.transfuse_corpus(
        [corpus_path],
        bundle_path,
        words_limit=word_limit,
        selector=index_builder
    )


def featurize_index(source: Path, destination: Path, workers: int = 2) -> None:
    CorpusBuilder.featurize_corpus(
        source,
        destination,
        [
            PyMorphyFeaturizer(),
            SlovnetFeaturizer(),
            SyntaxTreeFeaturizer(),
            SyntaxStatsFeaturizer()
        ],
        workers,
        True,
    )


def assemble(
        limit: int,
        corpus_path: Path,
        bundle_path: Path
        ) -> None:
    CorpusBuilder.assemble(
        corpus_path,
        bundle_path,
        limit
    )
    src = pd.read_parquet(bundle_path/'src.parquet')
    index = IndexBuilder.build_index_from_src(src)
    index.to_parquet(bundle_path/'index.parquet')
    print(index.groupby('split').size())
