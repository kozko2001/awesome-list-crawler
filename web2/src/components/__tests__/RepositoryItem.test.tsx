import { render, screen } from '@testing-library/react';
import { RepositoryItem } from '../RepositoryItem';
import { AppItem } from '@/types/api';

const mockItem: AppItem = {
  name: 'awesome-repo',
  description: 'A really awesome repository for testing',
  source: 'https://github.com/test/awesome-repo',
  list_name: 'awesome-javascript',
  list_source: 'https://github.com/test/awesome-javascript',
  time: '2024-01-15T10:30:00Z',
};

describe('RepositoryItem', () => {
  it('renders repository information correctly', () => {
    render(<RepositoryItem item={mockItem} />);
    
    // Check if repository name is rendered as a link
    const nameLink = screen.getByRole('link', { name: /awesome-repo/i });
    expect(nameLink).toBeInTheDocument();
    expect(nameLink).toHaveAttribute('href', mockItem.source);
    expect(nameLink).toHaveAttribute('target', '_blank');
    
    // Check if description is rendered
    expect(screen.getByText(mockItem.description)).toBeInTheDocument();
    
    // Check if list name is shown
    expect(screen.getByText(/from awesome-javascript/i)).toBeInTheDocument();
    
    // Check if date is formatted and shown
    expect(screen.getByText('1/15/2024')).toBeInTheDocument();
  });

  it('applies correct CSS classes for terminal styling', () => {
    const { container } = render(<RepositoryItem item={mockItem} />);
    
    const itemContainer = container.querySelector('[class*="border"]');
    expect(itemContainer).toHaveClass('border');
  });

  it('opens link in new tab with security attributes', () => {
    render(<RepositoryItem item={mockItem} />);
    
    const nameLink = screen.getByRole('link', { name: /awesome-repo/i });
    expect(nameLink).toHaveAttribute('rel', 'noopener noreferrer');
  });
});