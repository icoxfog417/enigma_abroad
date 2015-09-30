import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from pola.machine.topic_model.resource import PickleResource
from pola.machine.topic_model.resource import GensimResource
from pola.machine.topic_model import GTopicModel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make topic model from corpus.")

    parser.add_argument("path", type=str, help="path to corpus pickle file.")
    parser.add_argument("topics", type=int, help="number of topics.")
    parser.add_argument("--iter", type=int, default=5000, help="number of training iteration.")
    parser.add_argument("--burn", type=int, default=1000, help="number of burn.")
    parser.add_argument("--border", type=float, default=1000, help="minimum perplexity.")

    args = parser.parse_args()

    # make resource files
    fname = os.path.basename(args.path)
    make_path = lambda p: os.path.join(os.path.dirname(args.path), "./" + (os.path.splitext(fname)[0]) + "_" + p)
    r = GensimResource(make_path("model.gensim"))

    # document (corpus)
    p = PickleResource(args.path)
    doc = p.load()
    training, test = doc.split(right_rate_or_size=0.3, compact=False)

    model = None
    perplexity = 5000.0
    while perplexity > args.border:
        # make model
        model = GTopicModel(args.topics, training, resource=r)
        model.train(iter=args.iter, burn=args.burn)
        perplexity = model.perplexity(test)
        print("perplexity is {0} vs {1}".format(perplexity, args.border))

    print("model is created. perplexity is {0}/{1} (training/test)".format(model.perplexity(), model.perplexity(test)))

    model.save()
