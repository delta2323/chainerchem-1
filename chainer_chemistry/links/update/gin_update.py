import chainer
from chainer import functions

import chainer_chemistry
from chainer_chemistry.links.connection.graph_linear import GraphLinear


class GINUpdate(chainer.Chain):
    r"""GIN submodule for update part.

    Simplest implementation of Graph Isomorphism Network (GIN):
    2-layered MLP + ReLU
    no learnble epsilon

    Batch Normalization is not implemetned. instead we use droout

    # TODO: implement Batch Normalization
    # TODO: use GraphMLP instead of GraphLinears

    See: Xu, Hu, Leskovec, and Jegelka, \
        "How powerful are graph neural networks?", in ICLR 2019.

    Args:
        hidden_dim (int): dimension of feature vector associated to
            each atom
        dropout_ratio (float): ratio of dropout, insted of bach normlization
    """

    # TODO(mottodora): delete n_edge_type
    def __init__(self, in_channels=16, out_channels=None, n_edge_type=4,
                 dropout_ratio=0.5):
        if out_channels is None:
            out_channels = in_channels
        super(GINUpdate, self).__init__()
        with self.init_scope():
            # two Linear + RELU
            self.linear_g1 = GraphLinear(in_channels, out_channels)
            self.linear_g2 = GraphLinear(in_channels, out_channels)
        # end with
        self.dropout_ratio = dropout_ratio
        self.n_edge_type = n_edge_type
    # end-def

    def __call__(self, h, adj):
        """
        Describing a layer.

        Args:
            h (numpy.ndarray): minibatch by num_nodes by hidden_dim
                numpy array. local node hidden states
            adj (numpy.ndarray): minibatch by num_nodes by num_nodes 1/0 array.
                Adjacency matrices over several bond types

        Returns:
            updated h

        """

        # (minibatch, atom, ch)
        mb, atom, ch = h.shape

        # --- Message part ---
        # adj (mb, atom, atom)
        # fv   (minibatch, atom, ch)
        fv = chainer_chemistry.functions.matmul(adj, h)
        assert (fv.shape == (mb, atom, ch))

        # sum myself
        sum_h = fv + h
        assert (sum_h.shape == (mb, atom, ch))

        # apply MLP
        new_h = functions.relu(self.linear_g1(sum_h))
        if self.dropout_ratio > 0.0:
            new_h = functions.relu(
                functions.dropout(
                    self.linear_g2(new_h), ratio=self.dropout_ratio))
        else:
            new_h = functions.relu(self.linear_g2(new_h))

        # done???
        return new_h
