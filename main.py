from Generator import *
import sudoku, mnist, datetime
import numpy as np
import matplotlib.pyplot as plt

start_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

# get number image from MNIST dataset
test_images = mnist.test_images()
test_labels = mnist.test_labels()

# digit to image
def get_number_img(num, background=240):
  idxs = np.where(test_labels==num)[0]
  idx = np.random.choice(idxs, 1)
  img = test_images[idx].reshape((28, 28)).astype(np.int)
  img = background - img # make background white
  return img

# create board image
def create_board(s):
  board_img = np.empty((28*9, 28*9))
  board_img.fill(255)

  for i in range(9):
    for j in range(9):
      num = s[9 * i + j]
      
      if num is not None:
        num_img = get_number_img(num)
        rows = slice(28*(i%10), 28*((i+1)%10))
        cols = slice(28*(j%10), 28*((j+1)%10))
        board_img[rows, cols] = num_img

  return board_img

# visualize and save images
def visualize(board_imgs):
  for key, img in board_imgs.items():
    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)

    major_ticks = np.arange(0, 28*9, 28*3)
    minor_ticks = np.arange(0, 28*9, 28)
    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_yticks(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)

    ax.grid(True, which='both', color='k', linestyle='-')
    ax.grid(which='major', alpha=0.6, linewidth=1.5)
    ax.grid(which='minor', alpha=0.2)

    plt.xlim(0, 28*9)
    plt.ylim(28*9, 0)
    plt.imshow(img)
    plt.gray()
    plt.savefig('result/%s_%s.png' % (key, start_time))
  plt.show()

# main
# generate
gen = Generator()
quiz, answer = gen.generate(1) # 0-1-2-3
quiz = gen.get(quiz)
answer = gen.get(answer)

# another solver (sometimes not working properly)
# grid = sudoku.Grid(quiz)
# print("%s\n\n" % grid)
# grid.solve()
# print("\n%s\n" % grid)

quiz_img = create_board(quiz)
answer_img = create_board(answer)

visualize({
  'quiz': quiz_img,
  'answer': answer_img
})
