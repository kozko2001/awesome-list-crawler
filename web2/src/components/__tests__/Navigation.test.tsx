import { render, screen } from '@testing-library/react';
import { usePathname } from 'next/navigation';
import { Navigation } from '../Navigation';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>;

describe('Navigation', () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue('/');
  });

  it('renders all navigation links', () => {
    render(<Navigation />);
    
    expect(screen.getByRole('link', { name: /timeline/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /search/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /lucky/i })).toBeInTheDocument();
  });

  it('shows the logo with terminal styling', () => {
    render(<Navigation />);
    
    const logo = screen.getByText(/awesome-crawler/);
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveClass('glow-text');
  });

  it('highlights the active route', () => {
    mockUsePathname.mockReturnValue('/search');
    render(<Navigation />);
    
    const searchLink = screen.getByRole('link', { name: /search/i });
    const timelineLink = screen.getByRole('link', { name: /timeline/i });
    
    expect(searchLink).toHaveClass('text-terminal-green');
    expect(timelineLink).not.toHaveClass('text-terminal-green');
  });

  it('has correct href attributes', () => {
    render(<Navigation />);
    
    expect(screen.getByRole('link', { name: /timeline/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: /search/i })).toHaveAttribute('href', '/search');
    expect(screen.getByRole('link', { name: /lucky/i })).toHaveAttribute('href', '/lucky');
  });
});