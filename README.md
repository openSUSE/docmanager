# DocManager

The DocManager is a tool to manage meta-informations within DocBook5 documents.
It is possible to add new informations as well as editing and deleting. The
main advantage of this tool is the analyze feature. This feature creates a
table with all wanted informations. You can restrict the informations with a
light wight sql syntax.

## Usage

  1. **Adding or editing meta-informations**

    $ ./docmanager.py --set maintainer=test_name version=test_version --files test_file1.xml test_file2.xml

  2. **Deleting meta-infrmations**

    $ ./docmanager.py --set maintainer version --files test_file1.xml test_file2.xml

  3. **Get meta-informations**

    $ ./docmanager.py --get maintainer --files test_file1.xml test_file2.xml

    `Filename: test_file2.xml
    maintainer=test_name`
    
    For all informations use `all`.

  4. **Analyze meta-inforations**

   $ ./docmanager.py --analyse SELECT maintainer version WHERE maintainer=test_name --files test_file1.xml test_file2.xml

   `+----------------+---------+------------+
   |     Files      | version | maintainer |
   +----------------+---------+------------+
   | test_file1.xml |   1.0   | test_name  |
   | test_file2.xml |    -    | test_name  |
   +----------------+---------+------------+`
  
## Contribution

  1. Create a branch if you have exit otherwise fork it.
  2. Make your changes.
  3. Create a pull request.
  4. Done! Your changes will be reviewed as soon as possible.
