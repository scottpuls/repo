import shutil
import tempfile
import os

from electrum_trc import constants, blockchain
from electrum_trc.simple_config import SimpleConfig
from electrum_trc.blockchain import Blockchain, deserialize_pure_header, hash_header
from electrum_trc.util import bh2u, bfh, make_dir

from . import SequentialTestCase


class TestBlockchain(SequentialTestCase):

    HEADERS = {
        'A': deserialize_pure_header(bfh("01000000000000000000000000000000000000000000000000000000000000000000000096f12836f9a4d8029fea2c89ad06be01a9aaa6f3c3160c5867b00338f9098b0fdae5494dffff7f2002000000"), 0),
        'B': deserialize_pure_header(bfh("04010100d2a8d4eaa8ba68d79f1b92313b1f11ba539c3a540b1d84b9e669e1fce7a22454c5b3adce07063ce7a0c10586aaef7e57d9f1fcdbbd323b333beedfe5b1c3c7cd92153a5dffff7f2000000000"), 1),
        'C': deserialize_pure_header(bfh("04010100aeb03bd6576cce945215f99080a311c26c93165d830de2a54fa58a18de533519c8160f84c8da831592362da0bfcb89d6da871b32fcd906e8198267ea9d5b526593153a5dffff7f2000000000"), 2),
        'D': deserialize_pure_header(bfh("0401010084aa29cf0745a3c22c2f337934ea353dacbe9c703fd09a292fb326cf9f6312558a6c5acd18c144171edd3b3a9d2e7464a8922cb15647e70715220db6b8f0603293153a5dffff7f2000000000"), 3),
        'E': deserialize_pure_header(bfh("040101005434ea5acbd422bdee0bc85f539c69e500754007238b43d16362fedfec4ce7ce3f83f1588acc9b419a4f5b3ea8f12500d30280cad34acad00cc0a7be030704fb94153a5dffff7f2000000000"), 4),
        'F': deserialize_pure_header(bfh("04010100fea84de1e70b66f600cfc6662220fc1b619a77f89203c2c07f2ef33dc94ba1956ae4074f4c02a0aae2f758e2842938feb4898f9854867aacd451031bf374ec2594153a5dffff7f2000000000"), 5),
        'O': deserialize_pure_header(bfh("04010100ff601cc5e3df8f0590a9be43e9e762a0416253bc665bb7867a18ecb890f94c79c4dc044802c1146f2960366c8d6de8455d7523cec2ac3d39e212f1565a8f8f1794153a5dffff7f2000000000"), 6),
        'P': deserialize_pure_header(bfh("0401010046f5eee8a16352acfe929d27af9494f5738b408a4223016fb41d81a35d2cd3c75d0c56d1272b3efee929b2e4d764f37d9a12f4be9784017442e2fd13822e6534061b3a5dffff7f2000000000"), 7),
        'Q': deserialize_pure_header(bfh("04010100f782fb7ef21769f2fa7e304ba9cf2d7b17537e6dee773fa48c895bf47efebbea58fc9903c96106191f932fa92b4a5a304c88f77783717f2650b5e867fd03f1b5061b3a5dffff7f2000000000"), 8),
        'R': deserialize_pure_header(bfh("040101004c5d47a675e2a8af6261313494e83b7c7411222d72aa32ccbebc43ec5c74bde50445594bfe82354d4901f870dbf42ccdaf7438dcf5b88aab0bd8d814a515aaa9061b3a5dffff7f2000000000"), 9),
        'S': deserialize_pure_header(bfh("040101005e0559e20e90ccd9def4fbfa36aa6762fdd43e05939cef17849a224a991e3f190b21359445699cf68d8269017e8fb577deca79ae774c6c481e33874b21d7f814061b3a5dffff7f2000000000"), 10),
        'T': deserialize_pure_header(bfh("040101004b65a96d5833467f7b770c02bfbc592bc439471a9101e9fcb348e26fd10b65d4d80a86bdf598a2ecbbec1e9ba16f66fab619b2604e94e63c4489359d8b1a0c72061b3a5dffff7f2000000000"), 11),
        'U': deserialize_pure_header(bfh("040101009d2857ea52e62b41159f183c3961f54b751c0e7b124e9c0abec315416cea91d27e63ce93d701645c2f79cd90b3fcee717276c6af40f0ec5d7ef1e589ba3eb4bb061b3a5dffff7f2000000000"), 12),
        'G': deserialize_pure_header(bfh("04010100ff601cc5e3df8f0590a9be43e9e762a0416253bc665bb7867a18ecb890f94c79c4dc044802c1146f2960366c8d6de8455d7523cec2ac3d39e212f1565a8f8f1794153a5dffff7f2000000000"), 6),
        'H': deserialize_pure_header(bfh("0401010046f5eee8a16352acfe929d27af9494f5738b408a4223016fb41d81a35d2cd3c73a82a080149e5f04dee31e89d491cdb732ca643dfb1dce355bdf628dc21e8c6494153a5dffff7f2000000000"), 7),
        'I': deserialize_pure_header(bfh("04010100056e368100b10d9a715c7bdce7e31d1f8518d19b07a8aa6e6909569c5a80fec1842026f9d0a97e1d2d98da06b7f82c16cbbdf130d955bb807178986409caf3e095153a5dffff7f2000000000"), 8),
        'J': deserialize_pure_header(bfh("040101002a8a5bb4242a400052282bc9bc961d353b14dc59ea56349019891784e5224f95fe81e90dc6964e6e8926ae398636793ee28d3e3245532bdf6127fcbd146c932795153a5dffff7f2000000000"), 9),
        'K': deserialize_pure_header(bfh("0401010059c0544847fb33f0238b7a5eceed2ba19293c4b5c94276a273865e419c0fdcfb5679e53c102027584ed102ef69036e2862932a2fe2ccd6b79757666cb9d4e9c995153a5dffff7f2000000000"), 10),
        'L': deserialize_pure_header(bfh("0401010016c08d913ef7054acef3a5cd346c848243234645df69efc7bfb90553e453c4ccc1e463e6c8c1afa8d270b45be45d1abeaac0d09ed21f0a95db606dc8a9856ba595153a5dffff7f2000000000"), 11),
        'M': deserialize_pure_header(bfh("040101002a8a5bb4242a400052282bc9bc961d353b14dc59ea56349019891784e5224f95fe81e90dc6964e6e8926ae398636793ee28d3e3245532bdf6127fcbd146c932795153a5dffff7f2000000000"), 9),
        'N': deserialize_pure_header(bfh("0401010059c0544847fb33f0238b7a5eceed2ba19293c4b5c94276a273865e419c0fdcfbe39f9848d61df25b2b277089ccf9eef837b8381cc5ed6749e18598da87e490d678183a5dffff7f2000000000"), 10),
        'X': deserialize_pure_header(bfh("04010100f4444a20ddfab37b22dd0cb838128e437679606d20722d7c1e69bc9504445d558e891bfd831e2440ac56ce6c24b4ae1f333b46727bf513ebe125c5fa941a441d78183a5dffff7f2000000000"), 11),
        'Y': deserialize_pure_header(bfh("040101008618f830e30249a314cc453d15a3a518592efc984389164af3ee504ca6de9c12bfd55d093954d7a8e56dd5b1aa60c5b53e4d4005bb7548bb5e98837d7850feac78183a5dffff7f2000000000"), 12),
        'Z': deserialize_pure_header(bfh("04010100f2180d103da82c4c377b7ff2d90353f30bb14acf94de3fad271dcf5903d8ee6b066e7374b211cbe95f4f537e1e4816f55d15a410318ca8bd8542dbe540c73dd378183a5dffff7f2000000000"), 13),
    }
    # tree of headers:
    #                                            - M <- N <- X <- Y <- Z
    #                                          /
    #                             - G <- H <- I <- J <- K <- L
    #                           /
    # A <- B <- C <- D <- E <- F <- O <- P <- Q <- R <- S <- T <- U

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        constants.set_regtest()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        constants.set_mainnet()

    def setUp(self):
        super().setUp()
        self.data_dir = tempfile.mkdtemp()
        make_dir(os.path.join(self.data_dir, 'forks'))
        self.config = SimpleConfig({'electrum_path': self.data_dir})
        blockchain.blockchains = {}

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.data_dir)

    def _append_header(self, chain: Blockchain, header: dict):
        self.assertTrue(chain.can_connect(header))
        chain.save_header(header)

    def test_get_height_of_last_common_block_with_chain(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        self.assertEqual({chain_u:  8, chain_l: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11},             chain_l.get_parent_heights())

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self.assertEqual({chain_u:  8, chain_z: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11, chain_z: 8}, chain_l.get_parent_heights())
        self.assertEqual({chain_z: 13},             chain_z.get_parent_heights())
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_l))
        self.assertEqual(5, chain_l.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(5, chain_z.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(8, chain_l.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(8, chain_z.get_height_of_last_common_block_with_chain(chain_l))

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

        self.assertEqual({chain_u: 12, chain_z: 5}, chain_u.get_parent_heights())
        self.assertEqual({chain_l: 11, chain_z: 8}, chain_l.get_parent_heights())
        self.assertEqual({chain_z: 13},             chain_z.get_parent_heights())
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_l))
        self.assertEqual(5, chain_l.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(5, chain_u.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(5, chain_z.get_height_of_last_common_block_with_chain(chain_u))
        self.assertEqual(8, chain_l.get_height_of_last_common_block_with_chain(chain_z))
        self.assertEqual(8, chain_z.get_height_of_last_common_block_with_chain(chain_l))

    def test_parents_after_forking(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()
        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])

        self.assertEqual(None, chain_u.parent)

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        self._append_header(chain_l, self.HEADERS['L'])

        self.assertEqual(None,    chain_l.parent)
        self.assertEqual(chain_l, chain_u.parent)

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(None,    chain_z.parent)

        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])

        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(None,    chain_z.parent)

    def test_forking_and_swapping(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])

        # do checks
        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(0, chain_u.forkpoint)
        self.assertEqual(None, chain_u.parent)
        self.assertEqual(constants.net.GENESIS, chain_u._forkpoint_hash)
        self.assertEqual(None, chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_u.path())
        self.assertEqual(10 * 80, os.stat(chain_u.path()).st_size)
        self.assertEqual(6, chain_l.forkpoint)
        self.assertEqual(chain_u, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['G']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_794cf990b8ec187a86b75b66bc536241a062e7e943bea990058fdfe3c51c60ff_c7d32c5da3811db46f0123428a408b73f59494af279d92feac5263a1e8eef546"), chain_l.path())
        self.assertEqual(4 * 80, os.stat(chain_l.path()).st_size)

        self._append_header(chain_l, self.HEADERS['K'])

        # chains were swapped, do checks
        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_l, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_794cf990b8ec187a86b75b66bc536241a062e7e943bea990058fdfe3c51c60ff_c7d32c5da3811db46f0123428a408b73f59494af279d92feac5263a1e8eef546"), chain_u.path())
        self.assertEqual(4 * 80, os.stat(chain_u.path()).st_size)
        self.assertEqual(0, chain_l.forkpoint)
        self.assertEqual(None, chain_l.parent)
        self.assertEqual(constants.net.GENESIS, chain_l._forkpoint_hash)
        self.assertEqual(None, chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_l.path())
        self.assertEqual(11 * 80, os.stat(chain_l.path()).st_size)
        for b in (chain_u, chain_l):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

        self._append_header(chain_u, self.HEADERS['S'])
        self._append_header(chain_u, self.HEADERS['T'])
        self._append_header(chain_u, self.HEADERS['U'])
        self._append_header(chain_l, self.HEADERS['L'])

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])
        self._append_header(chain_z, self.HEADERS['Y'])
        self._append_header(chain_z, self.HEADERS['Z'])

        # chain_z became best chain, do checks
        self.assertEqual(3, len(blockchain.blockchains))
        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))
        self.assertEqual(0, chain_z.forkpoint)
        self.assertEqual(None, chain_z.parent)
        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
        self.assertEqual(None, chain_z._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
        self.assertEqual(14 * 80, os.stat(chain_z.path()).st_size)
        self.assertEqual(9, chain_l.forkpoint)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_954f22e584178919903456ea59dc143b351d96bcc92b285200402a24b45b8a2a_fbdc0f9c415e8673a27642c9b5c49392a12bedce5e7a8b23f033fb474854c059"), chain_l.path())
        self.assertEqual(3 * 80, os.stat(chain_l.path()).st_size)
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_794cf990b8ec187a86b75b66bc536241a062e7e943bea990058fdfe3c51c60ff_c7d32c5da3811db46f0123428a408b73f59494af279d92feac5263a1e8eef546"), chain_u.path())
        self.assertEqual(7 * 80, os.stat(chain_u.path()).st_size)
        for b in (chain_u, chain_l, chain_z):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))

        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
        self.assertEqual(hash_header(self.HEADERS['Z']), chain_z.get_hash(13))

    def test_doing_multiple_swaps_after_single_new_header(self):
        blockchain.blockchains[constants.net.GENESIS] = chain_u = Blockchain(
            config=self.config, forkpoint=0, parent=None,
            forkpoint_hash=constants.net.GENESIS, prev_hash=None)
        open(chain_u.path(), 'w+').close()

        self._append_header(chain_u, self.HEADERS['A'])
        self._append_header(chain_u, self.HEADERS['B'])
        self._append_header(chain_u, self.HEADERS['C'])
        self._append_header(chain_u, self.HEADERS['D'])
        self._append_header(chain_u, self.HEADERS['E'])
        self._append_header(chain_u, self.HEADERS['F'])
        self._append_header(chain_u, self.HEADERS['O'])
        self._append_header(chain_u, self.HEADERS['P'])
        self._append_header(chain_u, self.HEADERS['Q'])
        self._append_header(chain_u, self.HEADERS['R'])
        self._append_header(chain_u, self.HEADERS['S'])

        self.assertEqual(1, len(blockchain.blockchains))
        self.assertEqual(0, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        chain_l = chain_u.fork(self.HEADERS['G'])
        self._append_header(chain_l, self.HEADERS['H'])
        self._append_header(chain_l, self.HEADERS['I'])
        self._append_header(chain_l, self.HEADERS['J'])
        self._append_header(chain_l, self.HEADERS['K'])
        # now chain_u is best chain, but it's tied with chain_l

        self.assertEqual(2, len(blockchain.blockchains))
        self.assertEqual(1, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        chain_z = chain_l.fork(self.HEADERS['M'])
        self._append_header(chain_z, self.HEADERS['N'])
        self._append_header(chain_z, self.HEADERS['X'])

        self.assertEqual(3, len(blockchain.blockchains))
        self.assertEqual(2, len(os.listdir(os.path.join(self.data_dir, "forks"))))

        # chain_z became best chain, do checks
        self.assertEqual(0, chain_z.forkpoint)
        self.assertEqual(None, chain_z.parent)
        self.assertEqual(constants.net.GENESIS, chain_z._forkpoint_hash)
        self.assertEqual(None, chain_z._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "blockchain_headers"), chain_z.path())
        self.assertEqual(12 * 80, os.stat(chain_z.path()).st_size)
        self.assertEqual(9, chain_l.forkpoint)
        self.assertEqual(chain_z, chain_l.parent)
        self.assertEqual(hash_header(self.HEADERS['J']), chain_l._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['I']), chain_l._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_9_954f22e584178919903456ea59dc143b351d96bcc92b285200402a24b45b8a2a_fbdc0f9c415e8673a27642c9b5c49392a12bedce5e7a8b23f033fb474854c059"), chain_l.path())
        self.assertEqual(2 * 80, os.stat(chain_l.path()).st_size)
        self.assertEqual(6, chain_u.forkpoint)
        self.assertEqual(chain_z, chain_u.parent)
        self.assertEqual(hash_header(self.HEADERS['O']), chain_u._forkpoint_hash)
        self.assertEqual(hash_header(self.HEADERS['F']), chain_u._prev_hash)
        self.assertEqual(os.path.join(self.data_dir, "forks", "fork2_6_794cf990b8ec187a86b75b66bc536241a062e7e943bea990058fdfe3c51c60ff_c7d32c5da3811db46f0123428a408b73f59494af279d92feac5263a1e8eef546"), chain_u.path())
        self.assertEqual(5 * 80, os.stat(chain_u.path()).st_size)

        self.assertEqual(constants.net.GENESIS, chain_z.get_hash(0))
        self.assertEqual(hash_header(self.HEADERS['F']), chain_z.get_hash(5))
        self.assertEqual(hash_header(self.HEADERS['G']), chain_z.get_hash(6))
        self.assertEqual(hash_header(self.HEADERS['I']), chain_z.get_hash(8))
        self.assertEqual(hash_header(self.HEADERS['M']), chain_z.get_hash(9))
        self.assertEqual(hash_header(self.HEADERS['X']), chain_z.get_hash(11))

        for b in (chain_u, chain_l, chain_z):
            self.assertTrue(all([b.can_connect(b.read_header(i), False) for i in range(b.height())]))
