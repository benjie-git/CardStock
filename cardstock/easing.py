# Easing functions for use in animation

def ease_linear(progress):
    return progress


def ease_in(progress):
    return progress ** 2


def ease_out(progress):
    return 1 - (1 - progress) ** 2


def ease_in_out(progress):
    if progress < 0.5:
        return 2 * progress ** 2
    else:
        return 1 - 2 * (1 - progress) ** 2


def ease(progress_f, easing_type):
    if easing_type == "in":
        return ease_in(progress_f)
    elif easing_type == "out":
        return ease_out(progress_f)
    elif easing_type == "inout":
        return ease_in_out(progress_f)
    else:
        return ease_linear(progress_f)
