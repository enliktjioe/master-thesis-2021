import numpy

def group_rank(matrix, wg, reviews):
    group_scores = numpy.zeros(matrix.shape[1])

    for group_index in xrange(matrix.shape[1]):
        curr_score = 0

        fg = []
        volume = calc_volume(matrix, group_index)
        fg.append(volume)
        fg.append(calc_average_rating(matrix, group_index, reviews, volume))

        for i in xrange(len(fg)):
            curr_score += wg[i] * fg[i]
        group_scores[group_index] = curr_score

    return sorted(group_scores, reverse=True), sorted(range(len(group_scores)), key=lambda k: group_scores[k], reverse=True)

def calc_volume(matrix, group_index):
    result = 0
    for review_index in xrange(matrix.shape[0]):
        result += matrix[review_index][group_index]
    return result

def calc_average_rating(matrix, group_index, reviews, volume):
    denominator = 0
    for review_index in xrange(matrix.shape[0]):
        denominator += matrix[review_index][group_index] * reviews[review_index].rating * 1.0
    return volume / denominator