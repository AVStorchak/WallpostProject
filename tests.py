import unittest
import backend


class TestWallApp(unittest.TestCase):
    def test_id_conversion(self):
        """
        Verifies correct conversion of the passed user name
        """
        milonov = backend.get_query_id('milonov')
        durov_number = backend.get_query_id('1')
        durov_id = backend.get_query_id('id1')
        vkgames = backend.get_query_id('vkgames')
        self.assertEqual(milonov, 3011920)
        self.assertEqual(durov_number, 1)
        self.assertEqual(durov_id, 1)
        self.assertEqual(vkgames, -78616012)

    def test_upper_lower_conversion(self):
        """
        Verifies correct conversion of user names passed as
        uppercase/lowercase or their combination
        """
        milonov_low = backend.get_query_id('milonov')
        milonov_up = backend.get_query_id('MILONOV')
        milonov_mix = backend.get_query_id('mILonOv')
        self.assertEqual(milonov_low, milonov_up, milonov_mix)

    def test_all_posts(self):
        """
        Verifies correct downloading of a large batch of posts
        consisiting of the whole wall content
        *Must be adjusted accordingly, since new posts can be posted
        """
        timestamp = backend.get_query_timestamp('2000-1-1')
        milonov_posts = backend.load_posts(3011920, timestamp)
        self.assertEqual(len(milonov_posts), 2323)

    def test_recent_posts(self):
        """
        Verifies creation of a correct list of recent few posts
        *Must be adjusted accordingly, since new posts can be posted
        """
        name = 'milonov'
        date = '2020-1-22'
        query_id = backend.get_query_id(name)
        query_date = backend.get_query_timestamp(date)
        raw_milonov_posts = backend.load_posts(query_id, query_date)
        milonov_posts = backend.filter_posts(raw_milonov_posts, query_date)
        self.assertEqual(len(milonov_posts), 3)

    def test_post_data(self):
        """
        Verifies consistency between the created post data and
        the intial data.
        *Must be adjusted accordingly, since new posts can be posted
        and the number of likes and comments can change
        """
        name = 'vkgames'
        date = '15/12/2019'
        query_id = backend.get_query_id(name)
        query_date = backend.get_query_timestamp(date)
        all_posts = backend.load_posts(query_id, query_date)
        filtered_posts = backend.filter_posts(all_posts, query_date)

        self.assertEqual(filtered_posts[0]['likes'], 189)
        self.assertEqual(filtered_posts[1]['comments'], 80)
        self.assertEqual(filtered_posts[3]['apps'], 'https://vk.com/app5327745_254?ref=8')


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=3)
