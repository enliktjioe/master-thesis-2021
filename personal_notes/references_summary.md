## SAFE: A Simple Approach for Feature Extraction from App Descriptions and App Reviews (2017)
* Access from [SAFE]
* SAFE = Simple Approach for Feature Extraction
    * a novel uniform approach to extract app features from the single app pages, the single reviews and to match them
    * manually build 18 part of speech patterns and 5 sentence patterns that are frequently used in text referring to app features
    * apply these patterns with several text pre and post processing steps
    * major advantage
        * it doesn’t require large training and config data
* Identifying the SAFE Patterns
    * SAFE POS Patterns
        * analyze app description to identify commonly used POS patterns to denote app features
        * data crawling of 100 apps from Google Play Store
        * and then POS-tagged of the text using NLTK (Natural Language Tool KIt) and extracted all sentences
        * afterwards, each sentence rendered in a tool
        * manually looked at the sentences to find those patterns
    * SAFE Sentence Patterns
        * existing approaches often miss app features, if a single sentence contains a lot of indenpendent features.
        * for example: "send and receive images, videos, and stickers"
            * send/receive images; send/receive videos; send/receive stickers
* Automated Feature Extraction
    * Text Preprocessing
        * Input: single app desc or single review
        * First, sentence tokenization; All brackets and the text in between are removed as we observed that app features are prominently stated and that text in brackets often simply contains additional explanations.
        * Next, SAFE filters 3 types of sentences
            * contain URL
            * contain email addresses (for contact info)
            * contain quotations (most like to be quoted reviews)
        * Next, SAFE word-tokenizes each sentence without changing the order of the words
        * Thereafter, it removes stopwordds, and the name of the app from each tokenized sentence to reduce the number of words that might introduce noice in the feature extraction.
        * Final step, attach Part-of-Speech tags to each word token
    * Application of SAFE Patterns
        * Start with analyzing and decomposing the sentences based on the conjunctions, enumerations, and feature identifiers.
        * Then, SAFE applies the sentence patterns on the decomposed sentences to extract raw app features.
        * Finally, SAFE iterates through all extracted feature candidates, remove duplicates and noise such as identical word pairs (e.g. “email email” which matches the SAFE POS pattern Noun Noun)
    * Automated Feature Matching
        * First, single term level, two feature candidates are matching if each single term of them is equal, ignoring the order of the terms
            * for example, “send email” and “email send” are considered matching features
        * Second, SAFE uses the synonym sets of the words captured from WordNet to perform the second step of finding matching features.
            * for instance, “take photo” and “capture image” represent a match
        * Third, incorporates 2 similarity metrics
    * Eval questions:
        * How precise is SAFE when extracting features from appdescriptions and from app reviews?
        * How does SAFE perform compared to other state-of-the-art approaches?
        * How accurate can SAFE match the extracted featuresfrom the app descriptions and the reviews?
    * Evaluation Sets
        * Extraction from app descriptions
        * Extraction from app reviews
        * Extraction for feature matching
    * Conclusion
        * It called simple approach because it neither requires an apriori training with a large dataset nor a configuration of machine learning features and parameters
        * Precision up to 88% (56% average) and recall 70% (43% average)
        * An enabler for multiple app store analytics scenarios like monitoring app features’ health, the identification of features’ delta for gaining new insights, and feature recommendation and optimization
        * Also gives analysts a feature-based perspecive on their apps
    * Future
        * Research and fine-tuning of SAFE is needed
        * A subsequent of ML approach trained by developers can further improve the results





[SAFE]: https://ieeexplore.ieee.org/abstract/document/8048887/