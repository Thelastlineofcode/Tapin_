import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ReviewForm from '../components/ReviewForm';

describe('ReviewForm Component', () => {
  const mockListing = {
    id: 1,
    title: 'Test Listing',
  };

  const mockToken = 'test-token';
  const mockOnClose = vi.fn();
  const mockOnReviewAdded = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  it('renders review form with all elements', () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    expect(screen.getByText(/Review: Test Listing/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Rating/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Comment/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit Review/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
  });

  it('displays 5 star buttons', () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const starButtons = screen
      .getAllByRole('button')
      .filter((btn) => btn.getAttribute('aria-label')?.includes('star'));
    expect(starButtons).toHaveLength(5);
  });

  it('updates rating when star is clicked', async () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const threeStarButton = screen.getByRole('button', { name: /3 stars/i });
    await userEvent.click(threeStarButton);

    expect(screen.getByText('3 stars')).toBeInTheDocument();
  });

  it('allows comment input up to 500 characters', async () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const commentInput = screen.getByLabelText(/Comment/i);
    const testComment = 'Great experience!';

    await userEvent.type(commentInput, testComment);

    expect(commentInput).toHaveValue(testComment);
    expect(screen.getByText(`${testComment.length}/500`)).toBeInTheDocument();
  });

  it('calls onClose when Cancel button is clicked', async () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    await userEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('submits review with rating and comment', async () => {
    const mockResponse = {
      id: 1,
      rating: 5,
      comment: 'Excellent!',
      user_id: 1,
      listing_id: 1,
    };

    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    // Set rating to 5 stars
    const fiveStarButton = screen.getByRole('button', { name: /5 stars/i });
    await userEvent.click(fiveStarButton);

    // Add comment
    const commentInput = screen.getByLabelText(/Comment/i);
    await userEvent.type(commentInput, 'Excellent!');

    // Submit
    const submitButton = screen.getByRole('button', { name: /Submit Review/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        `http://127.0.0.1:5000/listings/${mockListing.id}/reviews`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
          body: JSON.stringify({ rating: 5, comment: 'Excellent!' }),
        }),
      );
    });

    expect(mockOnReviewAdded).toHaveBeenCalledWith(mockResponse);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('shows error when token is missing', async () => {
    render(
      <ReviewForm
        listing={mockListing}
        token={null}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const submitButton = screen.getByRole('button', { name: /Submit Review/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/Please log in/i);
    });

    expect(mockOnReviewAdded).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('shows error when API request fails', async () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'You have already reviewed this listing' }),
    });

    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const submitButton = screen.getByRole('button', { name: /Submit Review/i });
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/already reviewed/i);
    });

    expect(mockOnReviewAdded).not.toHaveBeenCalled();
    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('disables submit button while loading', async () => {
    globalThis.fetch.mockImplementationOnce(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({ id: 1, rating: 5 }),
              }),
            100,
          ),
        ),
    );

    render(
      <ReviewForm
        listing={mockListing}
        token={mockToken}
        onClose={mockOnClose}
        onReviewAdded={mockOnReviewAdded}
      />,
    );

    const submitButton = screen.getByRole('button', { name: /Submit Review/i });
    await userEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent(/Submitting/i);

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled();
    });
  });
});
