class Effect:
    def __init__(self, game, name, interval, activations, delay = 0, on_tick_update = "", on_start=None, on_tick=None, on_end=None, cleanup=None):
        self.name = name
        # wait this many ticks between activations
        self.interval = interval
        # how many times this effect activates before ending
        self.activations = activations
        # how many ticks to wait before the first activation.
        self.delay = delay
        # the update we see when this triggers on tick
        self.on_tick_update = on_tick_update
        # the tick the game was on when this effect was applied. on_tick runs when (current_tick - start_tick) % interval == 0
        self.start_tick = 0

        self.on_start_lambda = on_start or (lambda character: None)
        self.on_tick_lambda = on_tick or (lambda character: None)
        self.on_end_lambda = on_end or (lambda character: None)
        self.cleanup_lambda = cleanup or (lambda character: None)

    def on_start(self, character):
        # what happens to a character when they receive this effect
        if self.on_start:
            self.on_start_lambda(character)

    def on_tick(self, game, character):
        # what happens to a character every time the effect activates
        game.updates.append(self.on_tick_update)
        if self.on_tick:
            self.on_tick_lambda(character) 

    def on_end(self, character):
        # what happens to a character when the effect ends
        if self.on_end:
            self.on_end_lambda(character)
        self.cleanup_lambda(character)

    def cleanup(self, character):
        if self.cleanup:
            self.cleanup_lambda(character)
