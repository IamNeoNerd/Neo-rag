import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from './App';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

test('renders the app and handles a query', async () => {
  mockedAxios.post.mockResolvedValue({
    data: { synthesized_answer: 'This is a test response.' },
  });

  render(<App />);
  
  const input = screen.getByPlaceholderText(/ask a question/i);
  const button = screen.getByText(/submit/i);
  
  fireEvent.change(input, { target: { value: 'test query' } });
  fireEvent.click(button);
  
  await waitFor(() => {
    expect(screen.getByText(/this is a test response/i)).toBeInTheDocument();
  });
  
  expect(mockedAxios.post).toHaveBeenCalledWith('http://127.0.0.1:8000/retrieve', {
    query: 'test query',
  });
});
