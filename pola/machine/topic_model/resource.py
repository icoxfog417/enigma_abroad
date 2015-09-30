import os


class Resource():

    def __init__(self, path):
        self.path = path

    def load(self, **kwargs):
        raise Exception("You have to implements resource.get.")

    def save(self, obj):
        raise Exception("You have to implements resource.save.")

    def remove(self):
        raise Exception("You have to implements resource.remove.")

class PickleResource(Resource):

    def __init__(self, path):
        super().__init__(path)

    def load(self, **kwargs):
        obj = None
        with open(self.path, "rb") as f:
            import pickle
            obj = pickle.load(f)

        return obj

    def save(self, obj):
        with open(self.path, "wb") as f:
            import pickle
            pickle.dump(obj, f)

    def remove(self):
        if os.path.isfile(self.path):
            os.remove(self.path)


class MCMCResource(Resource):

    def __init__(self, path, db="pickle"):
        super().__init__(path)
        self.db = db

    def load(self, **kwargs):
        import pymc as pc
        m = kwargs["model"]

        if os.path.isfile(self.path):
            if self.db == "pickle":
                _db = pc.database.pickle.load(self.path)
                mcmc = pc.MCMC(m, db=_db)
            else:
                mcmc = pc.MCMC(m, db=self.db, dbname=self.path)
        else:
            mcmc = pc.MCMC(m)

        return mcmc

    def save(self, obj):
        if self.db == "ram":
            raise Exception("MCMC can not save when db='ram'")
        obj.db.close()

    def remove(self):
        if self.db == "pickle":
            if os.path.isfile(self.path):
                os.remove(self.path)


class GensimResource(Resource):

    def __init__(self, path):
        super().__init__(path)

    def load(self, **kwargs):
        m = None if "model" not in kwargs else kwargs["model"]
        if os.path.isfile(self.path):
            from gensim import models
            model = models.LdaModel.load(self.path)
            return model
        else:
            return m

    def save(self, obj):
        obj.save(self.path)

    def remove(self):
        if os.path.isfile(self.path):
            os.remove(self.path)


class FileResource(Resource):

    def __init__(self, path):
        super().__init__(path)

    def load(self, **kwargs):
        rows = []
        encoding = "utf-8" if "encoding" not in kwargs else kwargs["encoding"]
        separator = "\t" if "separator" not in kwargs else kwargs["separator"]
        deserializer = None if "deserializer" not in kwargs else kwargs["deserializer"]

        split = lambda x: x.replace("\r", "").replace("\n", "").split(separator)
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                lines = f.readlines()
                for ln in lines:
                    s = ln.decode(encoding)
                    items = split(s)
                    if deserializer:
                        obj = deserializer(*items)
                        rows.append(obj)
                    else:
                        rows.append(items)
        return rows

    def save(self, obj):
        with open(self.path, "wb") as f:
            for row in obj:
                line = ""
                if isinstance(row, list) or isinstance(row, tuple):
                    line = "\t".join(row) + os.linesep
                else:
                    line = row + os.linesep
                f.write(line.encode("utf-8"))

    def remove(self):
        if os.path.isfile(self.path):
            os.remove(self.path)
