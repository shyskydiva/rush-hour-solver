from solver.car import Car


def test_horizontal_car_cells():
    car = Car("X", 2, 0, 2, True)
    assert car.cells() == [(2, 0), (2, 1)]


def test_vertical_car_cells():
    car = Car("A", 0, 2, 3, False)
    assert car.cells() == [(0, 2), (1, 2), (2, 2)]


def test_moved_makes_a_new_car():
    car = Car("X", 2, 0, 2, True)
    moved = car.moved(2)
    assert moved.col == 2
    assert car.col == 0  # the original car didn't change