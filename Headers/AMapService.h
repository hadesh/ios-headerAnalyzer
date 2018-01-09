//
//  AMapSearchServices.h
//  AMapSearchKit
//
//  Created by xiaoming han on 15/6/18.
//  Copyright (c) 2015年 xiaoming han. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol AMapProtocol <NSObject>

- (void)aaaaa:(NSString *)aParams;

@end

@interface AMapService : NSObject

+ (AMapService *)sharedService;

/// API Key.
@property (nonatomic, copy) NSString *apiKey;

@end

@interface AMapServiceaaa (asd)
- (void)bbbbbbb;
@property (nonatomic, copy) NSString *aaaaa;

@end
