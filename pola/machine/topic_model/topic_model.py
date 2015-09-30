import numpy as np
import pymc as pc
from pola.machine.topic_model.model import Model
from pola.machine.topic_model.resource import MCMCResource


class TopicModel(Model):

    def __init__(self, topic_count, doc, resource, **kwargs):
        super(TopicModel, self).__init__(topic_count, doc, resource, **kwargs)
        self.core = pc.MCMC(self.core, db="pickle", dbname=self.resource.path)

    def build(self):
        K = self.topic_count
        V = len(self.doc.vocab_keys())  # number of words(vocab)
        D = len(self.doc)
        Wd = [self.doc.elements(i) for i in range(D)]
        Nd = [len(w) for w in Wd]

        alpha = np.ones(K) if "alpha" not in self.variables else self.variables["alpha"]
        beta = np.ones(V) if "beta" not in self.variables else self.variables["beta"]

        # model
        # word distribution for each topic
        phi = pc.Container([pc.CompletedDirichlet("phi_%i" % k, pc.Dirichlet("pphi_%i" % k, theta=beta)) for k in range(K)])

        # topic distribution in the docs
        theta = pc.Container([pc.CompletedDirichlet("theta_%i" % d, pc.Dirichlet("ptheta_%i" % d, theta=alpha)) for d in range(D)])

        # for each document, draw a topic z_m
        z = pc.Container([pc.Categorical("z_%i" % d, p=theta[d], size=Nd[d], value=np.random.randint(K, size=Nd[d])) for d in range(D)])

        # for each document, draw words, based on z_m
        w = pc.Container([pc.Categorical("w_%i_%i" % (d, i),
                                         p=pc.Lambda("phi_z_%i_%i" % (d, i), lambda _z=z[d][i], _phi=phi: _phi[_z]),
                                         value=Wd[d][i],
                                         observed=True
                                         )
                          for d in range(D) for i in range(Nd[d])])

        model = pc.Model([theta, phi, z, w])
        self.variables["phi"] = phi
        self.variables["theta"] = theta
        self.variables["z"] = z
        return model

    def train(self, iter=5000, burn=1000, verbose=False, **kwargs):
        self.core.sample(iter=iter, burn=burn)

        # show z_i(topic) after sampling (random walks) has ended
        # number of traces = iter – burn = 5000 – 1000 = 4000
        if verbose:
            for d in range(len(self.doc)):
                print(self.core.trace("z_%i" % d)[(iter - burn - 1)])

    def perplexity(self, test_doc=None):
        doc = test_doc if test_doc else self.doc
        # todo: have to consider about calculation of perplexity for test_doc
        return self._perplexity(doc, self.variables["theta"], self.variables["phi"])

    @classmethod
    def _perplexity(cls, doc, theta, phi):
        ps = []
        Nd = 0
        K = len(phi)
        for d in range(len(doc)):
            _topic = theta[d].value
            # topic * word probabilities
            wd = doc.elements(d)
            _words = np.array([[phi[t].value[0, w] for w in wd] for t in range(K)])
            _word_prob = np.sum(_topic * _words.T, axis=1)
            ps.append(- np.sum(np.log(_word_prob)))
            Nd += len(wd)

        p = np.exp(np.sum(ps) / Nd)
        return p

    def calc_distances(self, topic):
        phi = self.variables["phi"]
        base = phi[topic].value
        distances = [(i_p[0], self.kldiv(base, i_p[1].value)) for i_p in enumerate(phi) if i_p[0] != topic]
        distances = sorted(distances, key=lambda d: d[1])
        return distances

    def get_document_topics(self, index):
        z_d = self.variables["z"][index]
        topics = z_d.value
        rate = []
        for i in range(self.topic_count):
            r = sum([1 if t == i else 0 for t in topics]) / len(topics)
            rate.append((i, r))

        return rate

    def get_topic_documents(self, topic):
        z = self.variables["z"]
        spots = []
        for i, z in enumerate(z):
            ts = sum([1 if t == topic else 0 for t in z.value])
            if ts > 0:
                spots.append((i, ts))

        spots = sorted(spots, key=lambda s: s[1], reverse=True)
        return spots

    def get_topic_words(self, topic, topn=10):
        # todo: implement get_topic_words for pymc
        raise Exception("You have to implements how to get words in topic")
