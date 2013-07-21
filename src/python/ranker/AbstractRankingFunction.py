from utils import get_class


class AbstractRankingFunction:
    """Abstract base class for ranking functions."""

    def __init__(self,
                 ranker_arg_str,
                 ties,
                 feature_count,
                 init=None,
                 sample=None):

        self.feature_count = feature_count
        ranking_model_str = "ranker.model.Linear"
        for arg in ranker_arg_str:
            if arg.startswith("ranker.model"):
                ranking_model_str = arg
            else:
                self.ranker_type = float(arg)
        self.ranking_model = get_class(ranking_model_str)(feature_count)

        self.sample = getattr(__import__("utils"), sample)

        self.ties = ties
        self.w = self.ranking_model.initialize_weights(init)

    def score(self, features):
        return self.ranking_model.score(features, self.w.transpose())

    def get_candidate_weight(self, delta):
        u = self.sample(self.ranking_model.get_feature_count())
        return self.w + delta * u, u

    def init_ranking(self, query):
        raise NotImplementedError("Derived class needs to implement "
            "init_ranking.")

    def next(self):
        raise NotImplementedError("Derived class needs to implement "
            "next.")

    def next_det(self):
        raise NotImplementedError("Derived class needs to implement "
            "next_det.")

    def next_random(self):
        raise NotImplementedError("Derived class needs to implement "
            "next_random.")

    def get_document_probability(self, docid):
        raise NotImplementedError("Derived class needs to implement "
            "get_document_probability.")

    def rm_document(self, docid):
        raise NotImplementedError("Derived class needs to implement "
            "rm_document.")

    def document_count(self):
        raise NotImplementedError("Derived class needs to implement "
            "document_count.")

    def update_weights(self, w, alpha=None):
        """update weight vector"""
        if alpha == None:
            self.w = w
        else:
            self.w = self.w + alpha * w
