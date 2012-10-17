type ST = List[Int]
def encodeObject(o: T) = (new java.util.ArrayList(o)).asScala.toList
