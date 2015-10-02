import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from pola.machine.topic_model.resource import PickleResource
from pola.machine.topic_model.resource import GensimResource
from pola.machine.topic_model import GTopicModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make topic model from corpus.")

    parser.add_argument("topics", type=int, help="number of topics.")
    parser.add_argument("--till", type=int, help="upper number of topics.")
    parser.add_argument("--path", type=str, help="path to corpus pickle file.")
    parser.add_argument("--iter", type=int, default=5000, help="number of training iteration.")
    parser.add_argument("--burn", type=int, default=1000, help="number of burn.")
    parser.add_argument("--epoch", type=int, default=10, help="number of epoch.")

    args = parser.parse_args()
    path = args.path
    if not path:
        path = os.path.join(os.path.dirname(__file__), "../data/cityspots_doc_edited.pickle")

    # make resource files
    fname = os.path.basename(path)
    make_path = lambda p: os.path.join(os.path.dirname(path), "./" + (os.path.splitext(fname)[0]) + "_" + p)
    r = GensimResource(make_path("model.gensim"))

    # document (corpus)
    p = PickleResource(path)
    doc = p.load()
    training, test = doc.split(right_rate_or_size=0.3, compact=False)

    model = None
    perplexity = 1e5
    topics = [args.topics]
    if args.till:
        topics = range(args.topics, args.till + 1)

    for t in topics:
        print("topic count = {0}".format(t))
        for e in range(args.epoch):
            # make model
            m = GTopicModel(t, training, resource=r)
            m.train(iter=args.iter, burn=args.burn)
            p = m.perplexity(test)

            if p < perplexity:
                model = m
                perplexity = p

            print("\t epoch{0}: perplexity = {1}".format(e, p))

    print(
        "model is created. topics={0}, perplexity is {1}/{2} (training/test)".format(
            model.topic_count, model.perplexity(), model.perplexity(test))
    )

    model.save()
