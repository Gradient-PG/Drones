import numpy as np
import cv2 as cv


class IncorrectImageWrongChannelNumberException(Exception):
    """Wrong image is provided"""

    pass


def min_max_norm(image: np.ndarray) -> np.ndarray:
    """Apply min max norm on given image. If you want to process your image with openCV, you should use this norm
    instead of zero_one, due to being more useful. Reason of it is floating point inaccuracy, which might cause image
    distortion

    Parameters:
    ----------
    image: np.ndarray
        image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image
    """
    norm_image = np.zeros((image.shape[0], image.shape[1]))
    return cv.normalize(image, norm_image, 0, 255, cv.NORM_MINMAX)


def zero_one_norm(image: np.ndarray) -> np.ndarray:
    """Apply zero one pixel range. If you want to process your image later with neural network, you should use this norm
    instead of zero_one, due to being more useful. Reason of it is learning performance and to obtain better results of
    learning

    Parameters:
    ----------
    image: np.ndarray
        image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image
    """
    norm_image = np.zeros((image.shape[0], image.shape[1]))
    return cv.normalize(image, norm_image, 0, 1, cv.NORM_MINMAX)


def gray_norm(image: np.ndarray) -> np.ndarray:
    """Convert image to gray image

    Parameters:
    ----------
    image: np.ndarray
        image to be changed into gray

    Returns:
    ----------
    image: np.ndarray
        gray image
    """
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def histogram_equalization_gray(image: np.ndarray) -> np.ndarray:
    """Apply histogram normalization on single channel

    Parameters:
    ----------
    image: np.ndarray
        grayscale image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image

    Raises:
    ----------
        IncorrectImageWrongChannelNumberException: when image don't have single channel in image
    """
    if len(image.shape) > 2:
        raise IncorrectImageWrongChannelNumberException("Incorrect image, it should be gray")
    return cv.equalizeHist(image)


def histogram_equalization_luminance(image: np.ndarray) -> np.ndarray:
    """Apply histogram normalization on luminance channel, image should have 3 channels

    Parameters:
    ----------
    image: np.ndarray
        color image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image

    Raises:
    ----------
        IncorrectImageWrongChannelNumberException: when image don't have 3 channels in image
    """
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise IncorrectImageWrongChannelNumberException("It should have 3 channels")

    # convert from RGB color-space to YCrCb
    ycrcb_img = cv.cvtColor(image, cv.COLOR_BGR2YCrCb)

    # equalize the histogram of the Y channel
    ycrcb_img[:, :, 0] = cv.equalizeHist(ycrcb_img[:, :, 0])

    # convert back to RGB color-space from YCrCb
    return cv.cvtColor(ycrcb_img, cv.COLOR_YCrCb2BGR)


def histogram_equalization_color(image: np.ndarray) -> np.ndarray:
    """Apply histogram normalization on every image channel

    Parameters:
    ----------
    image: np.ndarray
        color image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image

    Raises:
    ----------
        IncorrectImageWrongChannelNumberException: when image don't have 3 channels in image
    """

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise IncorrectImageWrongChannelNumberException("It should have 3 channels")

    # segregate color streams
    b, g, r = cv.split(image)
    h_b, bin_b = np.histogram(b.flatten(), 256, [0, 256])
    h_g, bin_g = np.histogram(g.flatten(), 256, [0, 256])
    h_r, bin_r = np.histogram(r.flatten(), 256, [0, 256])
    # calculate cdf
    cdf_b = np.cumsum(h_b)
    cdf_g = np.cumsum(h_g)
    cdf_r = np.cumsum(h_r)

    # mask all pixels with value=0 and replace it with mean of the pixel values
    cdf_m_b = np.ma.masked_equal(cdf_b, 0)
    cdf_m_b = (cdf_m_b - cdf_m_b.min()) * 255 / (cdf_m_b.max() - cdf_m_b.min())
    cdf_final_b = np.ma.filled(cdf_m_b, 0).astype("uint8")

    cdf_m_g = np.ma.masked_equal(cdf_g, 0)
    cdf_m_g = (cdf_m_g - cdf_m_g.min()) * 255 / (cdf_m_g.max() - cdf_m_g.min())
    cdf_final_g = np.ma.filled(cdf_m_g, 0).astype("uint8")

    cdf_m_r = np.ma.masked_equal(cdf_r, 0)
    cdf_m_r = (cdf_m_r - cdf_m_r.min()) * 255 / (cdf_m_r.max() - cdf_m_r.min())
    cdf_final_r = np.ma.filled(cdf_m_r, 0).astype("uint8")

    # merge the images in the three channels
    img_b = cdf_final_b[b]
    img_g = cdf_final_g[g]
    img_r = cdf_final_r[r]

    img_out = cv.merge((img_b, img_g, img_r))
    return img_out


def image_centralization(image: np.ndarray) -> np.ndarray:
    """Centralize image value. For better result of this function you should normalize it by min_max norm firstly.
    If non-normalized image is provided, results may be unsatisfying.

    Parameters:
    ----------
    image: np.ndarray
        image to be centered

    Returns:
    ----------
    image: np.ndarray
        centered version of input image
    """
    return (image - image.mean()) * 2


def clahe_gray_norm(image: np.ndarray) -> np.ndarray:
    """Apply clahe method on gray image

    Parameters:
    ----------
    image: np.ndarray
        image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image

    Raises:
    ----------
        IncorrectImageWrongChannelNumberException: when image don't have single channel in image
    """
    if len(image.shape) > 2:
        raise IncorrectImageWrongChannelNumberException("Incorrect image, it should be gray")

    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def clahe_color_norm(image: np.ndarray) -> np.ndarray:
    """Apply clahe method on color image

    Parameters:
    ----------
    image: np.ndarray
        image to be normalized

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image

    Raises:
    ----------
        IncorrectImageWrongChannelNumberException: when image don't have 3 channels in image
    """
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise IncorrectImageWrongChannelNumberException("It should have 3 channels")

    lab = cv.cvtColor(image, cv.COLOR_BGR2LAB)
    lab_planes = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv.merge(lab_planes)

    return cv.cvtColor(lab, cv.COLOR_LAB2BGR)


def normalization(
    image: np.ndarray,
    minmax: bool = False,
    zero_one: bool = False,
    gray: bool = False,
    histogram_equalization: bool = False,
    centralization: bool = False,
    clahe: bool = False,
) -> np.ndarray:
    """Apply chosen norms on a given image. By default all norms are switched off

    Parameters:
    ----------
    image: np.ndarray
        image to be normalized
    minmax: bool
        apply minmax norm on image
    zero_one: bool
        apply zero_one norm on image
    gray: bool
        make image grayscale
    histogram_equalization: bool
        equalize histogram of all channels of image, depending on which scale image is
    centralization: bool
        make image central
    clahe: bool
        apply clahe method on image

    Returns:
    ----------
    image: np.ndarray
        normalized version of input image
    """
    norm_function_dict = {
        min_max_norm: minmax,
        zero_one_norm: zero_one,
        gray_norm: gray,
        image_centralization: centralization,
    }
    if gray:
        norm_function_dict[histogram_equalization_gray] = histogram_equalization
        norm_function_dict[clahe_gray_norm] = clahe
    else:
        norm_function_dict[histogram_equalization_color] = histogram_equalization
        norm_function_dict[histogram_equalization_luminance] = histogram_equalization
        norm_function_dict[clahe_color_norm] = clahe

    for norm_function, execute_norm in norm_function_dict.items():
        if execute_norm:
            image = norm_function(image)
    return image
