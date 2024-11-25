# Local Imports

class duplication_handler:
  __m_bloom_filter = []

  # Initializations

  # Helper Methods
  def validate_duplicate(self, p_key):
    if p_key not in self.__m_bloom_filter:
      return False
    else:
      return True

  def insert(self, p_url):
    self.__m_bloom_filter.append(p_url)

  def clear_filter(self):
    self.__m_bloom_filter.clear()
