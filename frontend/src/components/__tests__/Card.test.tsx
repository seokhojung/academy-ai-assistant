import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../ui/card';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders card with children', () => {
      render(
        <Card>
          <div data-testid="card-content">Card content</div>
        </Card>
      );
      expect(screen.getByTestId('card-content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(<Card className="custom-class">Content</Card>);
      expect(screen.getByRole('article')).toHaveClass('custom-class');
    });
  });

  describe('CardHeader', () => {
    it('renders header content', () => {
      render(
        <Card>
          <CardHeader>
            <div data-testid="header-content">Header</div>
          </CardHeader>
        </Card>
      );
      expect(screen.getByTestId('header-content')).toBeInTheDocument();
    });
  });

  describe('CardTitle', () => {
    it('renders title with correct text', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
          </CardHeader>
        </Card>
      );
      expect(screen.getByText('Test Title')).toBeInTheDocument();
    });
  });

  describe('CardDescription', () => {
    it('renders description with correct text', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
        </Card>
      );
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });
  });

  describe('CardContent', () => {
    it('renders content', () => {
      render(
        <Card>
          <CardContent>
            <div data-testid="content">Content</div>
          </CardContent>
        </Card>
      );
      expect(screen.getByTestId('content')).toBeInTheDocument();
    });
  });

  describe('CardFooter', () => {
    it('renders footer content', () => {
      render(
        <Card>
          <CardFooter>
            <div data-testid="footer-content">Footer</div>
          </CardFooter>
        </Card>
      );
      expect(screen.getByTestId('footer-content')).toBeInTheDocument();
    });
  });

  describe('Complete Card Structure', () => {
    it('renders complete card with all parts', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main content</p>
          </CardContent>
          <CardFooter>
            <button>Action</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('Main content')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /action/i })).toBeInTheDocument();
    });
  });
}); 