Description of the datasets used in our empirical studies.
----------------------------------------------------------
1. Each subject app has a folder.

2. Each app folder consists of three sub-folders, i.e., "trainL", "trainU" and "test". 

3. "trainL" contains the training data, "trainU" contains the unlabeled data, and "test" contains the test data.

4. "info.txt" contains informative review instances, while "non-info.txt" contains non-informative review instances.

5. Statistics of the four app datasets are shown in Table 4 in our manuscript.

6. Each review instance is represented by: [Number of tokens] [Rating] [Review text].
   For example, consider the review instance: "lenfive ratingone Can't change profile picture.", "lenfive" indicates that the review text has 5 tokens. "ratingone" means the user rating is 1.

7. In "swfitkey" folder, the file "swiftkey-case.txt" contains the data used in our case studies. Each review instance is represented by: [Id] [Timestamp] [Rating] [Review text]. 
   The unit of timestamp is millisecond.

If you have questions or find errors, please contact: hzzjucn@gmail.com