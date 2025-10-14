import React, { useState } from 'react';
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { Label } from '@/shared/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/select';
import { useSubmitClub } from '../hooks/useSubmitClub';

interface ClubSubmissionFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ClubSubmissionForm({ onSuccess, onCancel }: ClubSubmissionFormProps) {
  const [formData, setFormData] = useState({
    clubName: '',
    categories: '',
    clubPage: '',
    ig: '',
    discord: '',
    clubType: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { submitClub, isLoading, error } = useSubmitClub();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.clubName.trim()) newErrors.clubName = 'Club name is required';
    if (!formData.categories.trim()) newErrors.categories = 'Categories are required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await submitClub(formData);
      onSuccess?.();
    } catch (err) {
      console.error('Failed to submit club:', err);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Submit New Club</CardTitle>
        <CardDescription>
          Submit a new club for review. It will be published after admin approval.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Club Name */}
          <div className="space-y-2">
            <Label htmlFor="clubName">Club Name *</Label>
            <Input
              id="clubName"
              value={formData.clubName}
              onChange={(e) => handleInputChange('clubName', e.target.value)}
              placeholder="Enter club name"
              className={errors.clubName ? 'border-red-500' : ''}
            />
            {errors.clubName && <p className="text-sm text-red-500">{errors.clubName}</p>}
          </div>

          {/* Categories */}
          <div className="space-y-2">
            <Label htmlFor="categories">Categories *</Label>
            <Input
              id="categories"
              value={formData.categories}
              onChange={(e) => handleInputChange('categories', e.target.value)}
              placeholder="e.g., Sports, Academic, Social, Cultural"
              className={errors.categories ? 'border-red-500' : ''}
            />
            {errors.categories && <p className="text-sm text-red-500">{errors.categories}</p>}
          </div>

          {/* Club Type */}
          <div className="space-y-2">
            <Label htmlFor="clubType">Club Type</Label>
            <Select value={formData.clubType} onValueChange={(value) => handleInputChange('clubType', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select club type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="WUSA">WUSA</SelectItem>
                <SelectItem value="Athletics">Athletics</SelectItem>
                <SelectItem value="Student Society">Student Society</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Contact Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="clubPage">Club Website</Label>
              <Input
                id="clubPage"
                type="url"
                value={formData.clubPage}
                onChange={(e) => handleInputChange('clubPage', e.target.value)}
                placeholder="https://club-website.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ig">Instagram</Label>
              <Input
                id="ig"
                type="url"
                value={formData.ig}
                onChange={(e) => handleInputChange('ig', e.target.value)}
                placeholder="https://instagram.com/club_handle"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="discord">Discord</Label>
              <Input
                id="discord"
                type="url"
                value={formData.discord}
                onChange={(e) => handleInputChange('discord', e.target.value)}
                placeholder="https://discord.gg/invite-code"
              />
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-4">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
            )}
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Submitting...' : 'Submit Club'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
