import React, { useState } from 'react';
import { 
  Button, 
  Input, 
  Label, 
  Textarea, 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue,
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle,
  Alert, 
  AlertDescription,
  Calendar,
  Popover, 
  PopoverContent, 
  PopoverTrigger 
} from '@/shared/components/ui';
import { CalendarIcon, Upload, X } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/shared/lib/utils';
import { useSubmitEvent } from '@/features/events/hooks/useSubmitEvent';

interface EventSubmissionFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function EventSubmissionForm({ onSuccess, onCancel }: EventSubmissionFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    date: '',
    startTime: '',
    endTime: '',
    location: '',
    description: '',
    price: '',
    food: '',
    clubHandle: '',
    clubType: '',
    url: '',
    registration: false,
  });
  
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const { submitEvent, isLoading, error } = useSubmitEvent();

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors(prev => ({ ...prev, image: 'Please select a valid image file' }));
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({ ...prev, image: 'Image must be smaller than 10MB' }));
        return;
      }
      
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
      setErrors(prev => ({ ...prev, image: '' }));
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) newErrors.name = 'Event name is required';
    if (!formData.date) newErrors.date = 'Event date is required';
    if (!formData.startTime) newErrors.startTime = 'Start time is required';
    if (!formData.endTime) newErrors.endTime = 'End time is required';
    if (!formData.location.trim()) newErrors.location = 'Location is required';
    if (!imageFile) newErrors.image = 'Event image is required';
    
    // Validate date is in future
    if (formData.date && new Date(formData.date) <= new Date()) {
      newErrors.date = 'Event date must be in the future';
    }
    
    // Validate end time is after start time
    if (formData.startTime && formData.endTime && formData.startTime >= formData.endTime) {
      newErrors.endTime = 'End time must be after start time';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      const submitData = {
        ...formData,
        price: formData.price ? parseFloat(formData.price) : null,
        registration: formData.registration,
      };
      
      await submitEvent({ data: submitData, imageFile: imageFile! });
      onSuccess?.();
    } catch (err) {
      console.error('Failed to submit event:', err);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Submit New Event</CardTitle>
        <CardDescription>
          Submit an event for review. It will be published after admin approval.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          {/* Event Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Event Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter event name"
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Event Date *</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !formData.date && "text-muted-foreground",
                      errors.date && "border-red-500"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.date ? format(new Date(formData.date), "PPP") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={formData.date ? new Date(formData.date) : undefined}
                    onSelect={(date: Date | undefined) => handleInputChange('date', date ? date.toISOString().split('T')[0] : '')}
                    disabled={(date: Date) => date < new Date()}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              {errors.date && <p className="text-sm text-red-500">{errors.date}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="startTime">Start Time *</Label>
              <Input
                id="startTime"
                type="time"
                value={formData.startTime}
                onChange={(e) => handleInputChange('startTime', e.target.value)}
                className={errors.startTime ? 'border-red-500' : ''}
              />
              {errors.startTime && <p className="text-sm text-red-500">{errors.startTime}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="endTime">End Time *</Label>
              <Input
                id="endTime"
                type="time"
                value={formData.endTime}
                onChange={(e) => handleInputChange('endTime', e.target.value)}
                className={errors.endTime ? 'border-red-500' : ''}
              />
              {errors.endTime && <p className="text-sm text-red-500">{errors.endTime}</p>}
            </div>
          </div>

          {/* Location */}
          <div className="space-y-2">
            <Label htmlFor="location">Location *</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              placeholder="Enter event location"
              className={errors.location ? 'border-red-500' : ''}
            />
            {errors.location && <p className="text-sm text-red-500">{errors.location}</p>}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Describe the event..."
              rows={4}
            />
          </div>

          {/* Club Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="clubHandle">Club Handle</Label>
              <Input
                id="clubHandle"
                value={formData.clubHandle}
                onChange={(e) => handleInputChange('clubHandle', e.target.value)}
                placeholder="@club_handle"
              />
            </div>

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
          </div>

          {/* Additional Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="price">Price (optional)</Label>
              <Input
                id="price"
                type="number"
                step="0.01"
                min="0"
                value={formData.price}
                onChange={(e) => handleInputChange('price', e.target.value)}
                placeholder="0.00"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="food">Food Information</Label>
              <Input
                id="food"
                value={formData.food}
                onChange={(e) => handleInputChange('food', e.target.value)}
                placeholder="e.g., Free pizza, BYOF"
              />
            </div>
          </div>

          {/* URL */}
          <div className="space-y-2">
            <Label htmlFor="url">Event URL (optional)</Label>
            <Input
              id="url"
              type="url"
              value={formData.url}
              onChange={(e) => handleInputChange('url', e.target.value)}
              placeholder="https://..."
            />
          </div>

          {/* Registration */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="registration"
              checked={formData.registration}
              onChange={(e) => handleInputChange('registration', e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="registration">Registration required</Label>
          </div>

          {/* Image Upload */}
          <div className="space-y-2">
            <Label>Event Image *</Label>
            <div className="space-y-4">
              {!imagePreview ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <Label htmlFor="image" className="cursor-pointer">
                      <span className="text-blue-600 hover:text-blue-500">
                        Click to upload
                      </span>
                      <span className="text-gray-500"> or drag and drop</span>
                    </Label>
                    <Input
                      id="image"
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    PNG, JPG, WEBP up to 10MB
                  </p>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2"
                    onClick={removeImage}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
              {errors.image && <p className="text-sm text-red-500">{errors.image}</p>}
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
              {isLoading ? 'Submitting...' : 'Submit Event'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
