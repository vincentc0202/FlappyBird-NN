import pygame
import neat
import os
import time
import pickle
pygame.font.init()

from src.pipe import Pipe
from src.bird import Bird
from src.base import Base

WIN_HEIGHT = 800
WIN_WIDTH = 500

STAT_FONT = pygame.font.SysFont("arial", 50)
GEN = 0


def drawWindow(win, birds, pipes, base, score, gen):
    win.blit((pygame.image.load(os.path.join("imgs", "bg2.jpg"))), (0, 0))

    for bird in birds:
        bird.draw(win)

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    scoreText = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(scoreText, (WIN_WIDTH - 10 - scoreText.get_width(), 10))
    genText = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(genText, (10, 10))

    pygame.display.update()

def evaluateGenomes(genomes, config):
    global GEN
    GEN += 1
    clock = pygame.time.Clock()
    nets=[]
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 300))
        g.fitness = 0
        ge.append(g)

    pipes = [Pipe(600)]
    baseHeight = 730
    base = Base(baseHeight)
    score = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipeInd = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipeInd = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.02            #increase fitness the longer they stay alive -> encourages not to die

            #get the output from the nn (remember it uses tanh as the activation function)
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeInd].height), abs(bird.y - pipes[pipeInd].bottom)))
            if output[0] > 0.5:
                bird.jump()
        
        addPipe = False
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            pipe.move()

        #add a pipe and increment score after passing through one
        if addPipe:
            score += 1
            pipes.append(Pipe(600))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= baseHeight or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > 30:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break

        base.move()
        drawWindow(win, birds, pipes, base, score, GEN)


def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats) 

    winner = population.run(evaluateGenomes, 20)

    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, "config-feedforward.txt")
    run(configPath)