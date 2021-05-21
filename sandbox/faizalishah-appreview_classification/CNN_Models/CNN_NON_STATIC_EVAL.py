#! /usr/bin/env python

import numpy as np
import os
import time
import datetime
import data_helpers
import tensorflow as tf
from text_cnn_v2 import TextCNN
from tensorflow.contrib import learn
from sklearn.metrics import precision_recall_fscore_support
import csv


# Parameters
# ==================================================

# Model Hyperparameters
tf.flags.DEFINE_string("review_data", "../Review_Dataset/", "review dataset")
tf.flags.DEFINE_string("word2vec", "./GoogleNews-vectors-negative300.bin", "Word2vec file with pre-trained embeddings (default: None)")
tf.flags.DEFINE_integer("embedding_dim", 300, "Dimensionality of character embedding (default: 128)")
tf.flags.DEFINE_string("filter_sizes", "2,3,4", "Comma-separated filter sizes (default: '2,3,4')")
tf.flags.DEFINE_integer("num_filters", 128, "Number of filters per filter size (default: 128)")
tf.flags.DEFINE_float("dropout_keep_prob", 0.60, "Dropout keep probability (default: 0.5)")
tf.flags.DEFINE_float("l2_reg_lambda", 0.10, "L2 regularizaion lambda (default: 0.0)")

# Training parameters
tf.flags.DEFINE_integer("batch_size", 256, "Batch Size (default: 64)")
tf.flags.DEFINE_integer("num_epochs", 50, "Number of training epochs (default: 200)")
tf.flags.DEFINE_integer("evaluate_every", 100, "Evaluate model on dev set after this many steps (default: 100)")
tf.flags.DEFINE_integer("checkpoint_every",100, "Save model after this many steps (default: 100)")
# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
	print("{}={}".format(attr.upper(), value))
print("")


maxIteratioins = 10

average_precision_eval, average_recall_eval, average_fscore_eval= ([] for i in range(3))
average_precision_praise, average_recall_praise, average_fscore_praise= ([] for i in range(3))
average_precision_request,average_recall_request, average_fscore_request= ([] for i in range(3))
average_precision_bug, average_recall_bug, average_fscore_bug = ([] for i in range(3))
average_precision_others, average_recall_others, average_fscore_others = ([] for i in range(3))

# Data Preparatopn
# ==================================================

# Load data
#print("Loading data...")

with open('CNN_non_static_eval.csv','w') as f:
	writer = csv.writer(f,lineterminator='\n')
	writer.writerow(['Iteration','P','R','F1','P','R','F1','P','R','F1','P','R','F1','P','R','F1'])

	for i in range(0,maxIteratioins):
				
		print('############Iteration # %d###############' % (i+1))


		x_train_text, y_train,x_test_text,y_test = data_helpers.SplitDataIntoTrainTest(FLAGS.review_data)
	#x_text, y = data_helpers.SplitDataIntoTrainTest(FLAGS.review_data)

	# Build vocabulary
		max_document_length = max([len(x.split(" ")) for x in x_train_text])
		vocab_processor = learn.preprocessing.VocabularyProcessor(max_document_length)
		x_train = np.array(list(vocab_processor.fit_transform(x_train_text)))
		y_train = np.array(list(y_train))

		x_test = np.array(list(vocab_processor.transform(x_test_text)))
		y_test = np.array(list(y_test))
		#y_test = np.argmax(y_test, axis=1)
		#print(y_test)

		# # Randomly shuffle data
		# np.random.seed(10)
		# shuffle_indices = np.random.permutation(np.arange(len(y)))
		# x_shuffled = x[shuffle_indices]
		# y_shuffled = y[shuffle_indices]

		# Split train/test set
		# TODO: This is very crude, should use cross-validation
		# print("Vocabulary Size: {:d}".format(len(vocab_processor.vocabulary_)))
		# print("Train/Test split: {:d}/{:d}".format(len(y_train), len(y_test)))

		# Training
		# ==================================================

		with tf.Graph().as_default():
			session_conf = tf.ConfigProto(
			  allow_soft_placement=FLAGS.allow_soft_placement,
			  log_device_placement=FLAGS.log_device_placement)
			sess = tf.Session(config=session_conf)
			with sess.as_default():
				cnn = TextCNN(
					sequence_length=x_train.shape[1],
					num_classes=y_train.shape[1],
					vocab_size=len(vocab_processor.vocabulary_),
					embedding_size=FLAGS.embedding_dim,
					filter_sizes=list(map(int, FLAGS.filter_sizes.split(","))),
					num_filters=FLAGS.num_filters,
					l2_reg_lambda=FLAGS.l2_reg_lambda)

				# Define Training procedure
				global_step = tf.Variable(0, name="global_step", trainable=False)
				optimizer = tf.train.AdamOptimizer(1e-3)
				grads_and_vars = optimizer.compute_gradients(cnn.loss)
				train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

				#Keep track of gradient values and sparsity (optional)
				grad_summaries = []
				for g, v in grads_and_vars:
				    if g is not None:
				        grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
				        sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
				        grad_summaries.append(grad_hist_summary)
				        grad_summaries.append(sparsity_summary)
				grad_summaries_merged = tf.summary.merge(grad_summaries)

				# Output directory for models and summaries
				timestamp = str(int(time.time()))
				out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs", timestamp))
				print("Writing to {}\n".format(out_dir))

				#Summaries for loss and accuracy
				loss_summary = tf.summary.scalar("loss", cnn.loss)
				acc_summary = tf.summary.scalar("accuracy", cnn.accuracy)

				# Train Summaries
				train_summary_op = tf.summary.merge([loss_summary, acc_summary, grad_summaries_merged])
				train_summary_dir = os.path.join(out_dir, "summaries", "train")
				train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)

				#Dev summaries
				dev_summary_op = tf.summary.merge([loss_summary, acc_summary])
				dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
				dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, sess.graph)

				# Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
				checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
				checkpoint_prefix = os.path.join(checkpoint_dir, "model")
				if not os.path.exists(checkpoint_dir):
					os.makedirs(checkpoint_dir)
				saver = tf.train.Saver(tf.all_variables())

				# Write vocabulary
				#vocab_processor.save(os.path.join(out_dir, "vocab"))

				# Initialize all variables
				sess.run(tf.initialize_all_variables())
				# Initialize all variables
				#sess.run(tf.initialize_all_variables())
				if FLAGS.word2vec:
					# initial matrix with random uniform
					initW = np.random.uniform(-0.25,0.25,(len(vocab_processor.vocabulary_), FLAGS.embedding_dim))
					# load any vectors from the word2vec
					#print("Load word2vec file {}\n".format(FLAGS.word2vec))
					with open(FLAGS.word2vec, "rb") as f:
						header = f.readline()
						vocab_size, layer1_size = map(int, header.split())
						binary_len = np.dtype('float32').itemsize * layer1_size
						#print(vocab_size)
						#quit()
						for line in range(vocab_size):
							#print(line)
							word = []
							while True:
								ch = f.read(1).decode('latin-1')
								if ch == ' ':
									word = ''.join(word)
									break
								if ch != '\n':
									word.append(ch)
							#print(word)
							idx = vocab_processor.vocabulary_.get(word)
							#print("value of idx is" + str(idx));
							if idx != 0:
								#print("came to if");
								initW[idx] = np.fromstring(f.read(binary_len), dtype='float32')
							else:
								#print("came to else");
								f.read(binary_len)
					sess.run(cnn.W.assign(initW))
					#print("Ended")

				def ShowClassWisePerformance(true_y,pred_y):
				    true_y = np.argmax(true_y, 1)
				    precision, recall, fscore, support = precision_recall_fscore_support(true_y, pred_y,labels=[2,3,4])
				    print('Feature Evaluation -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[0],recall[0],fscore[0],support[0]))
				    print('Feature Request -> Prcision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[1], recall[1], fscore[1], support[1]))
				    print('Bug Report -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[2], recall[2], fscore[2], support[2]))
				    print('-----------------------------------------------------------------------------------------------')

				def train_step(x_batch, y_batch):
					"""
					A single training step
					"""
					feed_dict = {
					  cnn.input_x: x_batch,
					  cnn.input_y: y_batch,
					  cnn.dropout_keep_prob: FLAGS.dropout_keep_prob
					}
					_, step,loss, accuracy, pred_y= sess.run(
						[train_op, global_step, cnn.loss, cnn.accuracy,cnn.predicted_y],
						feed_dict)
					time_str = datetime.datetime.now().isoformat()
					print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
					#ShowClassWisePerformance(y_batch, pred_y)
					#train_summary_writer.add_summary(summaries, step)

				def dev_step(x_batch, y_batch, writer=None):
				    """
				    Evaluates model on a dev set
				    """
				    feed_dict = {
				      cnn.input_x: x_batch,
				      cnn.input_y: y_batch,
				      cnn.dropout_keep_prob: 1.0
				    }
				    step, summaries, loss, accuracy, pred_y = sess.run(
				        [global_step, dev_summary_op, cnn.loss, cnn.accuracy,cnn.predicted_y],
				        feed_dict)
				    time_str = datetime.datetime.now().isoformat()
				    print("{}: step {}, loss {:g}, acc {:g}".format(time_str, step, loss, accuracy))
				    ShowClassWisePerformance(y_batch, pred_y)
				    if writer:
				        writer.add_summary(summaries, step)

				# Generate batches
				batches = data_helpers.batch_iter(
					list(zip(x_train, y_train)), FLAGS.batch_size, FLAGS.num_epochs)
				# Training loop. For each batch...
				for batch in batches:
					#print(batch)
					x_batch, y_batch = zip(*batch)
					train_step(x_batch, y_batch)
					current_step = tf.train.global_step(sess, global_step)

					if current_step % FLAGS.evaluate_every == 0:
					    print("\nValidation on test-set ->")
					    print('-----------------------------------------------------------------------------------------------')
					    dev_step(x_test, y_test, writer=dev_summary_writer)
					    print("")
					if current_step % FLAGS.checkpoint_every == 0:
						path = saver.save(sess, checkpoint_prefix, global_step=current_step)
						print("Saved model checkpoint to {}\n".format(path))

		#print('######################Evaluation###############')

		# def ShowClassWisePerformance(true_y,pred_y):
		# 	precision, recall, fscore, support = precision_recall_fscore_support(true_y, pred_y,labels=[2,0,4,3,1])

		# 	print('class Evaluation -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[0],recall[0],fscore[0],support[0]))
		# 	print('class Praise -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[1],recall[1],fscore[1],support[1]))
		# 	print('class Feature Request -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[2], recall[2], fscore[2], support[2]))
		# 	print('class Bug Report -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[3], recall[3], fscore[3], support[3]))
		# 	print('class Others -> Precision : %.3f, Recall: %.3f, Fscore : %.3f, Support : %.3f' % (precision[4], recall[4], fscore[4], support[4]))
		# 	print("_______________________________________________________________________________________________________________________________")
		# 	#return precision,recall,fscore


		#print(checkpoint_dir)
		# checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
		# graph = tf.Graph()
		# with graph.as_default():
		# 	session_conf = tf.ConfigProto(
		# 	  allow_soft_placement=FLAGS.allow_soft_placement,
		# 	  log_device_placement=FLAGS.log_device_placement)
		# 	sess = tf.Session(config=session_conf)
		# 	with sess.as_default():
		# 		# Load the saved meta graph and restore variables
		# 		saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
		# 		saver.restore(sess, checkpoint_file)

		# 		# Get the placeholders from the graph by name
		# 		input_x = graph.get_operation_by_name("input_x").outputs[0]
		# 		# input_y = graph.get_operation_by_name("input_y").outputs[0]
		# 		dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

		# 		# Tensors we want to evaluate
		# 		predictions = graph.get_operation_by_name("output/predictions").outputs[0]
		# 		scores = graph.get_operation_by_name("output/scores").outputs[0]
		# 		# Generate batches for one epoch
		# 		batches = data_helpers.batch_iter(list(x_test), FLAGS.batch_size, 1, shuffle=False)
		# 		#top_k = 5
		# 		#if(2 < top_k):
		# 			#top_k = 2
		# 		#softmax = scores
		# 		softmax = tf.nn.sigmoid(scores, name="softmax")
		# 		#softmax = tf.nn.softmax(scores, name="softmax") #If you want probabilities instead of activation values that come in the score.
		# 		#softmax = tf.nn.sigmoid_cross_entropy_with_logits (logits=scores,labels=y_test, name="softmax")
		# 		#print("scores are")
		# 		#print(scores)
		# 		values, indices = tf.nn.top_k(softmax,sorted=True, k=5)
		# 		#print(values)
		# 		#print(indices)
		# 		label = []
		# 		confidence = []
		# 		# Collect the predictions here
		# 		all_predictions = []
		# 		#print("batch is ")
		# 		#print(batches[0])
		# 		for x_test_batch in batches:
		# 			batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
		# 			label, confidence = sess.run([indices, values],{input_x: x_test_batch, dropout_keep_prob: 1.0})
		# 			#print("The label ordering in descending order of confidence is - ")
		# 			#print(label)
		# 			#print("The confidence of the test input with each class in descending order is")
		# 			#print(confidence)
		# 			#print(confidence[0][0] + confidence[0][1])
		# 			#print(label[])
		# 			#print("For the batch")
		# 			#print(x_test_batch)
		# 			#print('batch predictions')
		# 			#print(batch_predictions)
		# 			all_predictions = np.concatenate([all_predictions, batch_predictions])
		# #         #print(all_predictions)
		# #         print("working**************")
		# # # Print accuracy if y_test is defined
		# if y_test is not None:
		# 	#print('Evaluation->')
		# 	#print(all_predictions.shape)
		# 	#print('y test')
		# 	#print(y_test.shape)
		# 	precision,recall,fscore  = ShowClassWisePerformance(y_test,all_predictions)
		# 	average_precision_eval.append(precision[0])
		# 	average_recall_eval.append(recall[0])
		# 	average_fscore_eval.append(fscore[0])
			
		# 	average_precision_praise.append(precision[1])
		# 	average_recall_praise.append(recall[1])
		# 	average_fscore_praise.append(fscore[1])
			
		# 	average_precision_request.append(precision[2])
		# 	average_recall_request.append(recall[2])
		# 	average_fscore_request.append(fscore[2])
			
		# 	average_precision_bug.append(precision[3])
		# 	average_recall_bug.append(recall[3])
		# 	average_fscore_bug.append(fscore[3])
			
		# 	average_precision_others.append(precision[4])
		# 	average_recall_others.append(recall[4])
		# 	average_fscore_others.append(fscore[4])

		# 	lst = [i+1,precision[0],recall[0],fscore[0],precision[1],recall[1],fscore[1]]
		# 	lst += [precision[2],recall[2],fscore[2],precision[3],recall[3],fscore[3]]
		# 	lst += [precision[4],recall[4],fscore[4]]

		# 	writer.writerow(lst)

		# 	print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature evaluation)" % (precision[0],recall[0],fscore[0]))
		# 	print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (praise)" % (precision[1],recall[1],fscore[1]))
		# 	print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature request)" % (precision[2],recall[2],fscore[2]))
		# 	print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (bug report)" % (precision[3],recall[3],fscore[3]))
		# 	print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (others)" % (precision[4],recall[4],fscore[4]))

			print('+++++++++++++++ITERATION #%d FINISHED++++++++++++++++++++++++++++' % (i+1))
			print("")

			#correct_predictions = float(sum(all_predictions == y_test))
			#print("Total number of test examples: {}".format(len(y_test)))
			#print("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))

		# Save the evaluation to a csv
		# predictions_human_readable = np.column_stack((np.array(x_test_text), all_predictions))
		# out_path = os.path.join(checkpoint_dir, "..", "prediction.csv")
		# print("Saving evaluation to {0}".format(out_path))
		# with open(out_path, 'w') as f:
		#     csv.writer(f).writerows(predictions_human_readable)

	# print("###########Average results for each class over %d iterations####################" % (maxIteratioins))
			
	# print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature evaluation)" % (np.mean(average_precision_eval),np.mean(average_recall_eval),np.mean(average_fscore_eval)))
	# print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (praise)" % (np.mean(average_precision_praise),np.mean(average_recall_praise),np.mean(average_fscore_praise)))
	# print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (feature request)" % (np.mean(average_precision_request),np.mean(average_recall_request),np.mean(average_fscore_request)))
	# print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (bug report)" % (np.mean(average_precision_bug),np.mean(average_recall_bug),np.mean(average_fscore_bug)))
	# print("Precision : %.3f, Recall : %.3f , Fscore : %.3f (others)" % (np.mean(average_precision_others),np.mean(average_recall_others),np.mean(average_fscore_others)))
